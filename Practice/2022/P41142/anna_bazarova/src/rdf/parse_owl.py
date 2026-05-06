from rdflib import Graph, Literal, RDF, URIRef

from src.get_data.structure import Beast


def parse_owl(path):
    # Create a Graph
    g = Graph()

    # Parse in an RDF file
    g.parse(path)

    # Loop through each triple in the graph (subj, pred, obj)
    for subj, pred, obj in g:
        # Check if there is at least one triple in the Graph
        if (subj, pred, obj) not in g:
            raise Exception("It better be!")

    # Print the number of "triples" in the Graph
    print(f"Graph g has {len(g)} statements.")
    # Prints: Graph g has 86 statements.

    # Print out the entire Graph in the RDF Turtle format
    print(g.serialize(format="turtle"))


def put_page(bst: Beast, g: Graph, lang_d: set):
    prefix = "http://www.semanticweb.org/annab/ontologies/2022/3/ontology"

    # добавление классов, на которые мы хоть можем распарсить
    beast_ont_class = URIRef(prefix+"#Beast")
    lang_ont_class = URIRef(prefix+"#Language")

    cr_ont_dp = URIRef(prefix+"#hasCRValue")
    init_ont_dp = URIRef(prefix+"#hasInitValue")
    xp_ont_dp = URIRef(prefix+"#hasXPValue")
    bma_ont_dp = URIRef(prefix+"#atk")
    cmb_ont_dp = URIRef(prefix+"#cmb")
    cmd_ont_dp = URIRef(prefix+"#cmd")
    ac_ont_dp = URIRef(prefix+"#hasACValue")
    ff_ont_dp = URIRef(prefix+"#hasFlatFootedValue")
    touch_ont_dp = URIRef(prefix+"#hasTouchValue")
    fort_ont_dp = URIRef(prefix+"#hasFortValue")
    ref_ont_dp = URIRef(prefix+"#hasRefValue")
    will_ont_dp = URIRef(prefix+"#hasWillValue")
    hp_ont_dp = URIRef(prefix+"#hasHPvalue")
    speed_ont_dp = URIRef(prefix+"#hasSpeedValue")
    str_ont_dp = URIRef(prefix+"#str")
    dex_ont_dp = URIRef(prefix+"#dex")
    int_ont_dp = URIRef(prefix+"#int")
    wis_ont_dp = URIRef(prefix+"#wis")
    con_ont_dp = URIRef(prefix+"#con")
    cha_ont_dp = URIRef(prefix+"#cha")

    # добавляем зверя
    uri = URIRef(prefix+f'#{bst.name}')
    g.add((uri, RDF.type, beast_ont_class))

    if bst.cr is not None:
        g.add((uri, cr_ont_dp, Literal(bst.cr)))
    if bst.initiative is not None:
        g.add((uri, init_ont_dp, Literal(bst.initiative)))
    if bst.xp is not None:
        g.add((uri, xp_ont_dp, Literal(bst.xp)))
    if bst.base_atk is not None:
        g.add((uri, bma_ont_dp, Literal(bst.base_atk)))
    if bst.cmb is not None:
        g.add((uri, cmb_ont_dp, Literal(bst.cmb)))
    if bst.cmd is not None:
        g.add((uri, cmd_ont_dp, Literal(bst.cmd)))
    if bst.ac is not None:
        g.add((uri, ac_ont_dp, Literal(bst.ac)))
    if bst.flat_footed is not None:
        g.add((uri, ff_ont_dp, Literal(bst.flat_footed)))
    if bst.touch is not None:
        g.add((uri, touch_ont_dp, Literal(bst.touch)))
    if bst.fort is not None:
        g.add((uri, fort_ont_dp, Literal(bst.fort)))
    if bst.ref is not None:
        g.add((uri, ref_ont_dp, Literal(bst.ref)))
    if bst.will is not None:
        g.add((uri, will_ont_dp, Literal(bst.will)))
    if bst.hp is not None:
        g.add((uri, hp_ont_dp, Literal(bst.hp)))
    if bst.speed is not None and bst.speed > 0:
        g.add((uri, speed_ont_dp, Literal(bst.speed)))
    if bst.streng is not None:
        g.add((uri, str_ont_dp, Literal(bst.streng)))
    if bst.dex is not None:
        g.add((uri, dex_ont_dp, Literal(bst.dex)))
    if bst.intell is not None:
        g.add((uri, int_ont_dp, Literal(bst.intell)))
    if bst.con is not None:
        g.add((uri, con_ont_dp, Literal(bst.con)))
    if bst.wis is not None:
        g.add((uri, wis_ont_dp, Literal(bst.wis)))
    if bst.cha is not None:
        g.add((uri, cha_ont_dp, Literal(bst.cha)))

    # languages
    lang_ont_op = URIRef(prefix+"#hasLanguages")
    for lang in bst.languages:
        lang_uri = URIRef(prefix + f'#{lang}')
        if lang not in lang_d:
            lang_d |= {lang}
            g.add((lang_uri, RDF.type, lang_ont_class))
        g.add((uri, lang_ont_op, lang_uri))
    # alignment
    alig_ont_op = URIRef(prefix+"#hasAlignment")
    ce = URIRef(prefix+"#chaoticEvil")
    cn = URIRef(prefix+"#chaoticNeutral")
    cg = URIRef(prefix+"#chaoticGood")
    ne = URIRef(prefix+"#neutralEvil")
    n = URIRef(prefix+"#trueNeutral")
    ng = URIRef(prefix+"#neutralGood")
    le = URIRef(prefix+"#lawfulEvil")
    ln = URIRef(prefix+"#lawfulNeutral")
    lg = URIRef(prefix+"#lawfulGood")
    if bst.alignment == "N":
        g.add((uri, alig_ont_op, n))
    elif bst.alignment == "CE":
        g.add((uri, alig_ont_op, ce))
    elif bst.alignment == "CN":
        g.add((uri, alig_ont_op, cn))
    elif bst.alignment == "CG":
        g.add((uri, alig_ont_op, cg))
    elif bst.alignment == "LE":
        g.add((uri, alig_ont_op, le))
    elif bst.alignment == "LN":
        g.add((uri, alig_ont_op, ln))
    elif bst.alignment == "LG":
        g.add((uri, alig_ont_op, lg))
    elif bst.alignment == "NE":
        g.add((uri, alig_ont_op, ne))
    elif bst.alignment == "NG":
        g.add((uri, alig_ont_op, ng))
    print("Добавлено в граф")
    return
