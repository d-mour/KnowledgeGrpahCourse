import argparse
import os
import random
from datetime import datetime
from collections import defaultdict, Counter

import numpy as np
from rdflib import Graph, URIRef, Literal, RDF, RDFS, XSD, Namespace


def load_triples_from_ttl(path: str):
    g = Graph()
    g.parse(path, format="turtle")

    triples = []
    literals = []
    for s, p, o in g:
        if isinstance(s, URIRef) and isinstance(p, URIRef) and isinstance(o, URIRef):
            triples.append((str(s), str(p), str(o)))
        elif isinstance(s, URIRef) and isinstance(p, URIRef) and isinstance(o, Literal):
            literals.append((str(s), str(p), o))

    return g, triples, literals


def extract_entity_dates(literals):
    date_map = {}
    for s, p, o in literals:
        if isinstance(o, Literal) and o.datatype in (XSD.date, XSD.dateTime):
            try:
                date_map.setdefault(s, []).append(datetime.fromisoformat(str(o)))
            except Exception:
                pass
    # keep max date per entity
    date_map = {k: max(v) for k, v in date_map.items() if v}
    return date_map


def build_index(triples):
    entities = set()
    relations = set()
    for s, p, o in triples:
        entities.add(s)
        entities.add(o)
        relations.add(p)
    ent2id = {e: i for i, e in enumerate(sorted(entities))}
    rel2id = {r: i for i, r in enumerate(sorted(relations))}
    id_triples = np.array([(ent2id[s], rel2id[p], ent2id[o]) for s, p, o in triples], dtype=np.int64)
    return ent2id, rel2id, id_triples


def split_by_date(triples, entity_dates, cutoff: datetime):
    train, test = [], []
    for s, p, o in triples:
        d = entity_dates.get(s)
        if d is not None:
            (train if d < cutoff else test).append((s, p, o))
        else:
            train.append((s, p, o))
    # fallback if test is empty
    if not test:
        rnd = list(range(len(triples)))
        random.shuffle(rnd)
        cut = max(1, len(rnd) // 10)
        test_idx = set(rnd[:cut])
        for i, t in enumerate(triples):
            (test if i in test_idx else train).append(t)
    return train, test


def split_train_valid_coverage(id_triples, valid_frac=0.1, seed=42):
    rng = np.random.default_rng(seed)
    n = len(id_triples)
    idx = np.arange(n)
    rng.shuffle(idx)
    v = max(1, int(valid_frac * n))
    valid_idx = set(idx[:v])
    train_idx = set(idx[v:])

    train = id_triples[list(train_idx)]
    valid = id_triples[list(valid_idx)]

    def ensure_coverage(a, b):
        a_ents = set(a[:, 0]).union(a[:, 2])
        b_ents = set(b[:, 0]).union(b[:, 2])
        # move triples so that every entity seen in a also appears at least once in b
        missing = a_ents - b_ents
        if not missing:
            return a, b
        a_list = list(map(tuple, a))
        rng.shuffle(a_list)
        for t in a_list:
            h, _, t_e = t
            if h in missing or t_e in missing:
                a = np.array([x for x in a_list if x != t], dtype=np.int64)
                b = np.vstack([b, np.array([t], dtype=np.int64)])
                b_ents.update([h, t_e])
                missing = a_ents - b_ents
                if not missing:
                    break
        return a, b

    train, valid = ensure_coverage(train, valid)
    valid, train = ensure_coverage(valid, train)
    return train, valid


class TransE:
    def __init__(self, n_entities, n_relations, dim=64, margin=1.0, lr=0.01, seed=42):
        rng = np.random.default_rng(seed)
        self.ent = rng.normal(0, 0.1, size=(n_entities, dim)).astype(np.float32)
        self.rel = rng.normal(0, 0.1, size=(n_relations, dim)).astype(np.float32)
        self.dim = dim
        self.margin = margin
        self.lr = lr

    def _score(self, h, r, t):
        return -np.linalg.norm(self.ent[h] + self.rel[r] - self.ent[t], axis=1)

    def _unit_normalize(self):
        n = np.linalg.norm(self.ent, axis=1, keepdims=True) + 1e-12
        self.ent /= n

    def fit(self, train_triples, epochs=50, batch_size=1024, neg_ratio=1, verbose=True, seed=42):
        rng = np.random.default_rng(seed)
        n = len(train_triples)
        for ep in range(1, epochs + 1):
            idx = np.arange(n)
            rng.shuffle(idx)
            total_loss = 0.0
            for start in range(0, n, batch_size):
                batch_idx = idx[start:start + batch_size]
                batch = train_triples[batch_idx]
                h = batch[:, 0]
                r = batch[:, 1]
                t = batch[:, 2]

                bs = len(batch)
                neg_h = h.copy()
                neg_t = t.copy()
                mask = rng.random(bs) < 0.5
                neg_h[mask] = rng.integers(0, self.ent.shape[0], size=mask.sum())
                neg_t[~mask] = rng.integers(0, self.ent.shape[0], size=(~mask).sum())

                pos_score = self._score(h, r, t)
                neg_score = self._score(neg_h, r, neg_t)
                loss = np.maximum(0.0, self.margin - pos_score + neg_score)
                total_loss += float(loss.mean())

                grad = (loss > 0).astype(np.float32)
                # compute gradients for embeddings
                # d/dh = unit((h + r - t)) * grad
                diff_pos = self.ent[h] + self.rel[r] - self.ent[t]
                diff_neg = self.ent[neg_h] + self.rel[r] - self.ent[neg_t]

                pos_dir = diff_pos / (np.linalg.norm(diff_pos, axis=1, keepdims=True) + 1e-12)
                neg_dir = diff_neg / (np.linalg.norm(diff_neg, axis=1, keepdims=True) + 1e-12)

                # updates
                for i in range(bs):
                    g = grad[i]
                    if g == 0:
                        continue
                    hi, ri, ti = h[i], r[i], t[i]
                    nhi, nti = neg_h[i], neg_t[i]
                    pd, nd = pos_dir[i], neg_dir[i]
                    # positive moves closer: subtract pd from h and r, add pd to t
                    self.ent[hi] -= self.lr * pd
                    self.rel[ri] -= self.lr * pd
                    self.ent[ti] += self.lr * pd
                    # negative moves apart: add nd to h and r, subtract nd from t
                    self.ent[nhi] += self.lr * nd
                    self.rel[ri] += self.lr * nd
                    self.ent[nti] -= self.lr * nd

            self._unit_normalize()
            if verbose and ep % 5 == 0:
                print(f"Epoch {ep}/{epochs} loss={total_loss/ (n//batch_size + 1):.4f}")

    def score_triples(self, triples):
        h, r, t = triples[:, 0], triples[:, 1], triples[:, 2]
        return self._score(h, r, t)


class DistMult:
    def __init__(self, n_entities, n_relations, dim=64, lr=0.01, seed=42):
        rng = np.random.default_rng(seed)
        self.ent = rng.normal(0, 0.1, size=(n_entities, dim)).astype(np.float32)
        self.rel = rng.normal(0, 0.1, size=(n_relations, dim)).astype(np.float32)
        self.dim = dim
        self.lr = lr

    def _score(self, h, r, t):
        # score = sum(h * r * t)
        return np.sum(self.ent[h] * self.rel[r] * self.ent[t], axis=1)

    def _unit_normalize(self):
        self.ent /= (np.linalg.norm(self.ent, axis=1, keepdims=True) + 1e-12)
        self.rel /= (np.linalg.norm(self.rel, axis=1, keepdims=True) + 1e-12)

    def fit(self, train_triples, epochs=50, batch_size=1024, neg_ratio=1, verbose=True, seed=42):
        rng = np.random.default_rng(seed)
        n = len(train_triples)
        for ep in range(1, epochs + 1):
            idx = np.arange(n)
            rng.shuffle(idx)
            total_loss = 0.0
            for start in range(0, n, batch_size):
                batch_idx = idx[start:start + batch_size]
                batch = train_triples[batch_idx]
                h = batch[:, 0]
                r = batch[:, 1]
                t = batch[:, 2]

                bs = len(batch)
                neg_h = h.copy()
                neg_t = t.copy()
                mask = rng.random(bs) < 0.5
                neg_h[mask] = rng.integers(0, self.ent.shape[0], size=mask.sum())
                neg_t[~mask] = rng.integers(0, self.ent.shape[0], size=(~mask).sum())

                pos_score = self._score(h, r, t)
                neg_score = self._score(neg_h, r, neg_t)
                margin = 1.0
                loss = np.maximum(0.0, margin - pos_score + neg_score)
                total_loss += float(loss.mean())

                grad = (loss > 0).astype(np.float32)
                for i in range(bs):
                    g = grad[i]
                    if g == 0:
                        continue
                    hi, ri, ti = int(h[i]), int(r[i]), int(t[i])
                    nhi, nti = int(neg_h[i]), int(neg_t[i])

                    # positive update: increase pos_score
                    self.ent[hi] += self.lr * g * (self.rel[ri] * self.ent[ti])
                    self.rel[ri] += self.lr * g * (self.ent[hi] * self.ent[ti])
                    self.ent[ti] += self.lr * g * (self.ent[hi] * self.rel[ri])

                    # negative update: decrease neg_score
                    if nhi != hi:  # corrupted head
                        self.ent[nhi] -= self.lr * g * (self.rel[ri] * self.ent[ti])
                    else:  # corrupted tail
                        self.ent[nti] -= self.lr * g * (self.ent[hi] * self.rel[ri])

            self._unit_normalize()
            if verbose and ep % 5 == 0:
                print(f"Epoch {ep}/{epochs} loss={total_loss/ (n//batch_size + 1):.4f}")

    def score_triples(self, triples):
        h, r, t = triples[:, 0], triples[:, 1], triples[:, 2]
        return self._score(h, r, t)


def add_reciprocal_triples(id_triples, n_relations):
    # add inverse relation r+R and flipped head/tail
    inv = id_triples.copy()
    inv[:, [0, 2]] = inv[:, [2, 0]]
    inv[:, 1] = inv[:, 1] + n_relations
    augmented = np.vstack([id_triples, inv])
    return augmented

def build_constraints(id_triples, n_relations):
    heads = {r: set() for r in range(n_relations)}
    tails = {r: set() for r in range(n_relations)}
    for h, r, t in id_triples.tolist():
        heads[int(r)].add(int(h))
        tails[int(r)].add(int(t))
    return {r: {
        "heads": np.array(sorted(list(hs)), dtype=np.int64),
        "tails": np.array(sorted(list(ts)), dtype=np.int64)
    } for r, (hs, ts) in enumerate(zip(heads.values(), tails.values()))}


def evaluate_ranking(model: TransE, valid_triples, train_triples, n_entities, negatives=50, seed=123, constraints=None):
    rng = np.random.default_rng(seed)
    train_set = {tuple(t) for t in map(tuple, train_triples.tolist())}
    mrr = 0.0
    mr = 0.0
    hits10 = 0
    for i in range(len(valid_triples)):
        h, r, t = valid_triples[i]
        candidates = []
        candidates.append((h, r, t, True))
        for _ in range(negatives):
            if rng.random() < 0.5:
                if constraints is not None and r in constraints:
                    pool = constraints[r]["heads"]
                    hh = int(pool[rng.integers(0, len(pool))]) if len(pool) else rng.integers(0, n_entities)
                else:
                    hh = rng.integers(0, n_entities)
                cand = (hh, r, t)
            else:
                if constraints is not None and r in constraints:
                    pool = constraints[r]["tails"]
                    tt = int(pool[rng.integers(0, len(pool))]) if len(pool) else rng.integers(0, n_entities)
                else:
                    tt = rng.integers(0, n_entities)
                cand = (h, r, tt)
            if cand in train_set:
                continue
            candidates.append((*cand, False))
        cand_arr = np.array([c[:3] for c in candidates], dtype=np.int64)
        scores = model.score_triples(cand_arr)
        pos_score = scores[0]
        rank = int(1 + np.sum(scores > pos_score))
        mr += rank
        mrr += 1.0 / rank
        hits10 += int(rank <= 10)
    n = len(valid_triples)
    return {"MR": mr / n, "MRR": mrr / n, "Hits@10": hits10 / n}


def kmeans(X, k, iters=100, seed=42):
    rng = np.random.default_rng(seed)
    n = X.shape[0]
    idx = rng.choice(n, size=k, replace=False)
    C = X[idx].copy()
    for _ in range(iters):
        d = ((X[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)
        y = d.argmin(axis=1)
        for j in range(k):
            pts = X[y == j]
            if len(pts) > 0:
                C[j] = pts.mean(axis=0)
    return y, C


def adjusted_rand_score(labels_true, labels_pred):
    labels_true = np.asarray(labels_true)
    labels_pred = np.asarray(labels_pred)
    classes, class_idx = np.unique(labels_true, return_inverse=True)
    clusters, cluster_idx = np.unique(labels_pred, return_inverse=True)
    n_classes = classes.shape[0]
    n_clusters = clusters.shape[0]
    n = labels_true.shape[0]
    # contingency table
    cont = np.zeros((n_classes, n_clusters), dtype=np.int64)
    for i in range(n):
        cont[class_idx[i], cluster_idx[i]] += 1
    sum_comb_c = sum(np.sum(cont, axis=1) * (np.sum(cont, axis=1) - 1) // 2)
    sum_comb_k = sum(np.sum(cont, axis=0) * (np.sum(cont, axis=0) - 1) // 2)
    sum_comb = sum(cont.flatten() * (cont.flatten() - 1) // 2)
    comb_n = n * (n - 1) // 2
    expected = (sum_comb_c * sum_comb_k) / comb_n if comb_n else 0.0
    max_index = 0.5 * (sum_comb_c + sum_comb_k)
    denom = max_index - expected
    if denom == 0:
        return 0.0
    return float((sum_comb - expected) / denom)


def pca_2d(X):
    Xc = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    Z = Xc @ Vt[:2].T
    return Z


def save_embeddings(out_dir, ent2id, rel2id, ent_emb, rel_emb):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entities.tsv"), "w", encoding="utf-8") as f:
        for e, i in sorted(ent2id.items(), key=lambda x: x[1]):
            f.write(e + "\t" + "\t".join(map(str, ent_emb[i].tolist())) + "\n")
    with open(os.path.join(out_dir, "relations.tsv"), "w", encoding="utf-8") as f:
        for r, i in sorted(rel2id.items(), key=lambda x: x[1]):
            f.write(r + "\t" + "\t".join(map(str, rel_emb[i].tolist())) + "\n")


def softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / (e.sum(axis=1, keepdims=True) + 1e-12)


def train_softmax_classifier(X_train, y_train, X_val, y_val, lr=0.1, epochs=200, reg=1e-4, seed=42):
    rng = np.random.default_rng(seed)
    n, d = X_train.shape
    k = int(y_train.max()) + 1
    W = rng.normal(0, 0.01, size=(d, k))
    for ep in range(1, epochs + 1):
        scores = X_train @ W
        P = softmax(scores)
        Y = np.zeros_like(P)
        Y[np.arange(n), y_train] = 1.0
        grad = X_train.T @ (P - Y) / n + reg * W
        W -= lr * grad
        if ep % 50 == 0:
            acc = (P.argmax(axis=1) == y_train).mean()
            val_acc = (softmax(X_val @ W).argmax(axis=1) == y_val).mean()
            print(f"Softmax ep{ep} train_acc={acc:.3f} val_acc={val_acc:.3f}")
    return W


def train_mlp_classifier(X_train, y_train, X_val, y_val, hidden=256, lr=0.01, epochs=500, reg=1e-4, seed=42):
    rng = np.random.default_rng(seed)
    n, d = X_train.shape
    k = int(y_train.max()) + 1
    W1 = rng.normal(0, 0.02, size=(d, hidden))
    b1 = np.zeros((hidden,))
    W2 = rng.normal(0, 0.02, size=(hidden, k))
    b2 = np.zeros((k,))
    batch = max(32, min(512, n))
    for ep in range(1, epochs + 1):
        idx = np.arange(n)
        rng.shuffle(idx)
        for start in range(0, n, batch):
            ids = idx[start:start + batch]
            Xb = X_train[ids]
            yb = y_train[ids]
            H = Xb @ W1 + b1
            H = np.maximum(H, 0)
            scores = H @ W2 + b2
            P = softmax(scores)
            Y = np.zeros_like(P)
            Y[np.arange(len(ids)), yb] = 1.0
            ds = (P - Y) / len(ids)
            dW2 = H.T @ ds + reg * W2
            db2 = ds.sum(axis=0)
            dH = ds @ W2.T
            dH[H <= 0] = 0
            dW1 = Xb.T @ dH + reg * W1
            db1 = dH.sum(axis=0)
            W2 -= lr * dW2
            b2 -= lr * db2
            W1 -= lr * dW1
            b1 -= lr * db1
        if ep % 100 == 0:
            Hv = np.maximum(X_val @ W1 + b1, 0)
            Pv = softmax(Hv @ W2 + b2)
            val_acc = (Pv.argmax(axis=1) == y_val).mean()
            print(f"MLP ep{ep} val_acc={val_acc:.3f}")
    return (W1, b1, W2, b2)


def _collect_labels(g, EX, class_uri, predicate_uri):
    labeled = []
    dates = {}
    for s, _, _ in g.triples((None, RDFS.label, None)):
        pass
    for s, _, _ in g.triples((None, RDF.type, class_uri)):
        tier = None
        for _s, _p, _o in g.triples((s, predicate_uri, None)):
            tier = str(_o)
            break
        if not tier:
            continue
        dt = None
        for _s, _p, _o in g.triples((s, EX.lastReleaseDate, None)):
            try:
                dt = datetime.fromisoformat(str(_o))
            except Exception:
                pass
            break
        dates[str(s)] = dt
        labeled.append((str(s), tier))
    return labeled, dates


def classification_technology_maturity(g, ent2id, ent_emb, cutoff_dt, seed=42, target_predicate="hasMaturityTier", args=None):
    from rdflib import Namespace
    EX = Namespace("https://stackknowledge.org/stackkg#")
    predicate_uri = getattr(EX, target_predicate)
    labeled, dates = _collect_labels(g, EX, EX.Technology, predicate_uri)

    if not labeled:
        print("No labeled Technology with hasMaturityTier found for classification.")
        return

    tiers = sorted({t for _, t in labeled})
    tier2id = {t: i for i, t in enumerate(tiers)}

    # split by date
    X_train_idx, y_train, X_test_idx, y_test = [], [], [], []
    for ent, t in labeled:
        if ent not in ent2id:
            continue
        idx = ent2id[ent]
        dt = dates.get(ent)
        if dt is not None and dt >= cutoff_dt:
            X_test_idx.append(idx)
            y_test.append(tier2id[t])
        else:
            X_train_idx.append(idx)
            y_train.append(tier2id[t])

    if not X_train_idx or not X_test_idx:
        # Fallback to stratified random split over all labeled technologies
        print("Classification: fallback to stratified random split (date split empty).")
        all_idx = []
        all_y = []
        for ent, t in labeled:
            if ent in ent2id:
                all_idx.append(ent2id[ent])
                all_y.append(tier2id[t])
        all_idx = np.array(all_idx, dtype=np.int64)
        all_y = np.array(all_y, dtype=np.int64)
        if len(all_idx) < 2:
            print("Classification: not enough samples after fallback; skipping.")
            return
        rng = np.random.default_rng(seed)
        X_train_idx, y_train, X_test_idx, y_test = [], [], [], []
        for cls in sorted(set(all_y)):
            cls_idx = np.where(all_y == cls)[0]
            rng.shuffle(cls_idx)
            cut = max(1, int(0.8 * len(cls_idx)))
            tr = cls_idx[:cut]
            te = cls_idx[cut:] if len(cls_idx) - cut > 0 else cls_idx[-1:]
            for i in tr:
                X_train_idx.append(int(all_idx[i]))
                y_train.append(int(all_y[i]))
            for i in te:
                X_test_idx.append(int(all_idx[i]))
                y_test.append(int(all_y[i]))

    Xtr = ent_emb[np.array(X_train_idx)]
    Xte = ent_emb[np.array(X_test_idx)]
    ytr = np.array(y_train, dtype=np.int64)
    yte = np.array(y_test, dtype=np.int64)

    # normalize embedding features
    def norm(X):
        n = np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
        return X / n
    Xtr = norm(Xtr)
    Xte = norm(Xte)

    if args and getattr(args, 'clf', 'softmax') == 'mlp':
        W1, b1, W2, b2 = train_mlp_classifier(Xtr, ytr, Xte, yte, hidden=256, lr=0.01, epochs=500, reg=1e-4, seed=seed)
        Hv = np.maximum(Xte @ W1 + b1, 0)
        acc = (softmax(Hv @ W2 + b2).argmax(axis=1) == yte).mean()
    else:
        W = train_softmax_classifier(Xtr, ytr, Xte, yte, lr=0.5, epochs=400, reg=1e-4, seed=seed)
        acc = (softmax(Xte @ W).argmax(axis=1) == yte).mean()

    # baselines
    maj = Counter(ytr).most_common(1)[0][0]
    maj_acc = (yte == maj).mean()

    # one-hot baseline over simple categorical relations (without using target)
    cat_preds = [EX.usesLanguage, EX.hasRuntimePerformanceTier, EX.hasCommunitySupportTier, EX.hasEcosystemRichnessTier]
    # build vocab
    vocab = {}
    def feats_for(ent_uri):
        feats = []
        for pp in cat_preds:
            for _s, _p, _o in g.triples((URIRef(ent_uri), pp, None)):
                feats.append(str(_o))
        return feats
    for ent, _ in labeled:
        for f in feats_for(ent):
            if f not in vocab:
                vocab[f] = len(vocab)
    def build_X(indices):
        X = np.zeros((len(indices), len(vocab)), dtype=np.float32)
        ents = [list(ent2id.keys())[list(ent2id.values()).index(i)] for i in indices]
        for row, ent_uri in enumerate(ents):
            for f in feats_for(ent_uri):
                X[row, vocab[f]] = 1.0
        return X
    Xtr_oh = build_X(X_train_idx)
    Xte_oh = build_X(X_test_idx)
    if Xtr_oh.shape[1] > 0:
        Wb = train_softmax_classifier(Xtr_oh, ytr, Xte_oh, yte, lr=0.5, epochs=400, reg=1e-4, seed=seed)
        oh_acc = (softmax(Xte_oh @ Wb).argmax(axis=1) == yte).mean()
    else:
        oh_acc = float('nan')

    # Hybrid: concatenate embeddings + one-hot if available
    if Xtr_oh.shape[1] > 0:
        Xtr_h = np.hstack([Xtr, Xtr_oh])
        Xte_h = np.hstack([Xte, Xte_oh])
        if args and getattr(args, 'clf', 'softmax') == 'mlp':
            W1h, b1h, W2h, b2h = train_mlp_classifier(Xtr_h, ytr, Xte_h, yte, hidden=256, lr=0.01, epochs=500, reg=1e-4, seed=seed)
            Hvh = np.maximum(Xte_h @ W1h + b1h, 0)
            hyb_acc = (softmax(Hvh @ W2h + b2h).argmax(axis=1) == yte).mean()
        else:
            Wh = train_softmax_classifier(Xtr_h, ytr, Xte_h, yte, lr=0.5, epochs=400, reg=1e-4, seed=seed)
            hyb_acc = (softmax(Xte_h @ Wh).argmax(axis=1) == yte).mean()
    else:
        hyb_acc = float('nan')

    print(f"Classification (predict {target_predicate} for Technology):")
    print(f" - Test accuracy (embeddings): {acc:.3f}")
    print(f" - Baseline majority: {maj_acc:.3f}")
    if not np.isnan(oh_acc):
        print(f" - Baseline one-hot (attributes): {oh_acc:.3f}")
    if not np.isnan(hyb_acc):
        print(f" - Hybrid (embeddings + one-hot): {hyb_acc:.3f}")


def link_prediction_demo(model, g, ent2id, rel2id, id_train, id_test, predicate_uri: str, seed=42, negatives=50, constraints=None):
    # pick test triples with given predicate
    pred_id = rel2id.get(predicate_uri)
    if pred_id is None:
        print(f"Predicate not found in relations: {predicate_uri}")
        return
    mask = id_test[:, 1] == pred_id
    test_subset = id_test[mask]
    if len(test_subset) == 0:
        print("No test triples for the chosen predicate; skipping link prediction demo.")
        return
    # evaluate with object corruption only
    metrics = evaluate_ranking(model, test_subset, id_train, n_entities=len(ent2id), negatives=negatives, seed=seed, constraints=constraints)
    print(f"Link Prediction for predicate={predicate_uri} (object corruption): {metrics}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ttl", type=str, default="stackkg_large.ttl")
    parser.add_argument("--cutoff", type=str, default="2025-06-01")
    parser.add_argument("--dim", type=int, default=64)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch", type=int, default=1024)
    parser.add_argument("--negatives", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--eval_negatives", type=int, default=50)
    parser.add_argument("--out", type=str, default="embeddings")
    parser.add_argument("--cluster", action="store_true")
    parser.add_argument("--classify", action="store_true")
    parser.add_argument("--cluster_pred", type=str, default="hasMaturityTier", help="EX predicate local name for clustering labels")
    parser.add_argument("--classify_pred", type=str, default="hasMaturityTier", help="EX predicate local name for classification labels")
    parser.add_argument("--clf", type=str, default="softmax", choices=["softmax", "mlp"], help="Classifier for classification task")
    parser.add_argument("--model", type=str, default="transe", choices=["transe", "distmult"])
    parser.add_argument("--add_reciprocals", action="store_true")
    parser.add_argument("--type_constrained", action="store_true", help="Use type-constrained negatives for eval and LP")
    parser.add_argument("--lp_predicate", type=str, default="https://stackknowledge.org/stackkg#hasRuntimePerformanceTier")
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)

    g, triples, literals = load_triples_from_ttl(args.ttl)
    print(f"Loaded {len(triples)} object triples, {len(literals)} literal triples")

    entity_dates = extract_entity_dates(literals)
    cutoff = datetime.fromisoformat(args.cutoff)
    train_trp, test_trp = split_by_date(triples, entity_dates, cutoff)
    print(f"Split by date: train={len(train_trp)} test={len(test_trp)}")

    ent2id, rel2id, id_all = build_index(triples)
    id_train = np.array([(ent2id[s], rel2id[p], ent2id[o]) for s, p, o in train_trp], dtype=np.int64)
    id_test = np.array([(ent2id[s], rel2id[p], ent2id[o]) for s, p, o in test_trp], dtype=np.int64)

    if args.add_reciprocals:
        id_train = add_reciprocal_triples(id_train, n_relations=len(rel2id))
        # expand rel2id with inverse names for consistency on save
        inv_rel2id = {}
        base = len(rel2id)
        for r, i in list(rel2id.items()):
            inv_rel2id[r + "_INV"] = i + base
        # merge
        rel2id = {**rel2id, **inv_rel2id}

    id_train_main, id_valid = split_train_valid_coverage(id_train, valid_frac=0.1, seed=args.seed)
    print(f"Train-main={len(id_train_main)} Valid={len(id_valid)} Test={len(id_test)}")

    if args.model == "transe":
        model = TransE(n_entities=len(ent2id), n_relations=len(rel2id), dim=args.dim, margin=1.0, lr=0.01, seed=args.seed)
    else:
        model = DistMult(n_entities=len(ent2id), n_relations=len(rel2id), dim=args.dim, lr=0.01, seed=args.seed)
    model.fit(id_train_main, epochs=args.epochs, batch_size=args.batch, neg_ratio=args.negatives, verbose=True, seed=args.seed)

    constraints = build_constraints(id_train_main, n_relations=len(rel2id)) if args.type_constrained else None
    metrics = evaluate_ranking(model, id_valid, id_train_main, n_entities=len(ent2id), negatives=args.eval_negatives, seed=args.seed, constraints=constraints)
    print("Validation metrics:", metrics)

    save_embeddings(args.out, ent2id, rel2id, model.ent, model.rel)
    print(f"Saved embeddings to {args.out}")

    if args.cluster:
        EX = Namespace("https://stackknowledge.org/stackkg#")
        tech_type = str(EX.Technology)
        label_map = {}
        tier_map = {}
        for s, p, o in g.triples((None, RDFS.label, None)):
            if isinstance(s, URIRef) and isinstance(o, Literal):
                label_map[str(s)] = str(o)
        target_pred = getattr(EX, args.cluster_pred)
        for s, p, o in g.triples((None, RDF.type, None)):
            if str(o) == tech_type:
                tier = None
                for _, pp, oo in g.triples((s, target_pred, None)):
                    tier = str(oo)
                    break
                if tier:
                    tier_map[str(s)] = tier
        tech_ids = []
        tiers = []
        names = []
        for ent, tier in tier_map.items():
            if ent in ent2id:
                tech_ids.append(ent2id[ent])
                tiers.append(tier)
                names.append(label_map.get(ent, ent))
        if tech_ids:
            X = model.ent[np.array(tech_ids)]
            uniq_tiers = sorted(set(tiers))
            k = len(uniq_tiers)
            pred, _ = kmeans(X, k=k, iters=50, seed=args.seed)
            ari = adjusted_rand_score(np.array([uniq_tiers.index(t) for t in tiers]), pred)
            print(f"Clustering KMeans(k={k}) ARI={ari:.4f} on Technology by {args.cluster_pred}")
            # Save 2D projection CSV for easy plotting elsewhere
            Z = pca_2d(X)
            os.makedirs(args.out, exist_ok=True)
            with open(os.path.join(args.out, "clustering_pca2d.tsv"), "w", encoding="utf-8") as f:
                f.write("name\ttier\tx\ty\tcluster\n")
                for i in range(len(names)):
                    f.write(f"{names[i]}\t{tiers[i]}\t{Z[i,0]:.6f}\t{Z[i,1]:.6f}\t{pred[i]}\n")
            print(f"Saved clustering projection to {os.path.join(args.out, 'clustering_pca2d.tsv')}")

    if args.classify:
        classification_technology_maturity(g, ent2id, model.ent, cutoff, seed=args.seed, target_predicate=args.classify_pred, args=args)

    if args.lp_predicate:
        link_prediction_demo(model, g, ent2id, rel2id, id_train_main, id_test, args.lp_predicate, seed=args.seed, negatives=args.eval_negatives, constraints=constraints)


if __name__ == "__main__":
    main()
