using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using System.Xml;

namespace OwlBooks
{
    class RatingRegistry
    {
        readonly Dictionary<string, RatingEntry> _byWorkId = new Dictionary<string, RatingEntry>();
        readonly Dictionary<string, RatingEntry> _byBookId = new Dictionary<string, RatingEntry>();

        public int WorksCount { get { return _byWorkId.Count; } }
        public int BooksCount { get { return _byBookId.Count; } }

        public void Add(string workId, string bookId, int rating)
        {
            if (!_byWorkId.TryGetValue(workId, out var workEntry))
                _byWorkId.Add(workId, workEntry = new RatingEntry(workId, null));

            workEntry.Append(rating);

            if (!_byBookId.TryGetValue(bookId, out var bookEntry))
                _byBookId.Add(bookId, bookEntry = new RatingEntry(workId, bookId));

            bookEntry.Append(rating);
        }

        public bool TryGetByWorkId(string id, out RatingEntry entry)
        {
            return _byWorkId.TryGetValue(id, out entry);
        }

        public bool TryGetByBookId(string id, out RatingEntry entry)
        {
            return _byBookId.TryGetValue(id, out entry);
        }

        public void SaveTo(string byWorkFileName, string byBookFileName)
        {
            this.WriteData(_byWorkId.Values, byWorkFileName);
            this.WriteData(_byBookId.Values, byBookFileName);
        }

        private void WriteData(IEnumerable<RatingEntry> items, string fileName)
        {
            using (var writer = new StreamWriter(fileName))
            {
                foreach (var item in items)
                {
                    writer.WriteLine(item.ToDataString());
                }
                writer.WriteLine();
            }
        }
    }

    class RatingEntry
    {
        public string WorkId { get; }
        public string BookId { get; }

        public double RatingValue { get; private set; }
        private int v0, v1, v2, v3, v4, v5;

        public HashSet<string> Isbn { get; private set; } = new HashSet<string>();
        public HashSet<string> Genres { get; private set; } = new HashSet<string>();

        public RatingEntry(string workId, string bookId)
        {
            this.WorkId = workId;
            this.BookId = bookId;
        }

        public void Append(int value)
        {
            switch (value)
            {
                case 0: v0++; break;
                case 1: v1++; break;
                case 2: v2++; break;
                case 3: v3++; break;
                case 4: v4++; break;
                case 5: v5++; break;
                default: return;
            }
            this.RatingValue = (double)(v5 * 5 + v4 * 4 + v3 * 3 + v2 * 2 + v1 * 1) / (double)(v0 + v1 + v2 + v3 + v4 + v5);
        }

        public string ToDataString()
        {
            return $"{this.WorkId}\t{this.BookId}\t{this.RatingValue:00.00}\t[{string.Join(", ", this.Isbn)}]\t[{string.Join(", ", this.Genres)}]";
        }
    }

    static class KnownTypeKeys
    {
        public const string author = "/type/author";
        public const string redirect = "/type/redirect";
        public const string delete = "/type/delete";
        public const string edition = "/type/edition";
        public const string page = "/type/page";
        public const string i18n = "/type/i18n";
        public const string language = "/type/language";
        public const string library = "/type/library";
        public const string subject = "/type/subject";
        public const string template = "/type/template";
        public const string work = "/type/work";
        public const string macro = "/type/macro";
        public const string type = "/type/type";
        public const string rawtext = "/type/rawtext";
        public const string volume = "/type/volume";
        public const string @object = "/type/object";
        public const string backreference = "/type/backreference";
        public const string about = "/type/about";
        public const string home = "/type/home";
        public const string local_id = "/type/local_id";
        public const string permission = "/type/permission";
        public const string i18n_page = "/type/i18n_page";
        public const string series = "/type/series";
        public const string user = "/type/user";
        public const string usergroup = "/type/usergroup";
        public const string collection = "/type/collection";
        public const string scan_record = "/type/scan_record";
        public const string doc = "/type/doc";
        public const string uri = "/type/uri";
        public const string place = "/type/place";
        public const string scan_location = "/type/scan_location";
    }

    static class xmlns
    {
        public const string owl = "http://www.w3.org/2002/07/owl#";
        public const string rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
        public const string xml = "http://www.w3.org/XML/1998/namespace";
        public const string xsd = "http://www.w3.org/2001/XMLSchema#";
        public const string rdfs = "http://www.w3.org/2000/01/rdf-schema#";
        public const string books = "http://www.semanticweb.org/books#";
        public const string ontobooks = "http://www.semanticweb.org/e1izabeth/ontobooks#";
    }

    interface IEntityInfo<T>
        where T : class, IEntityInfo<T>
    {
        string Id { get; }
        string Title { get; }

        void MergeFrom(T other);
    }

    class EntityRegistry<T>
        where T : class, IEntityInfo<T>
    {
        private readonly Dictionary<string, T> _byId = new Dictionary<string, T>();
        private readonly Dictionary<string, T> _byTitle = new Dictionary<string, T>();

        public IEnumerable<T> GetEntities()
        {
            return _byId.Values;
        }

        public T Resolve(T entity)
        {
            if (string.IsNullOrWhiteSpace(entity.Id) && string.IsNullOrWhiteSpace(entity.Title))
                return null;

            T existing = null;
            if (existing == null && !string.IsNullOrEmpty(entity.Id) && _byId.TryGetValue(entity.Id, out var x))
                existing = x;
            if (existing == null && !string.IsNullOrEmpty(entity.Title) && _byTitle.TryGetValue(entity.Title, out var y))
                existing = y;

            if (existing == null)
            {
                existing = entity;
            }
            else
            {
                existing.MergeFrom(entity);
            }

            if (existing.Title != null && existing.Title.ToLower().StartsWith("http"))
                throw new InvalidOperationException("Invalid title");

            if (!string.IsNullOrEmpty(existing.Id) && !_byId.ContainsKey(existing.Id))
                _byId.Add(existing.Id, existing);
            if (!string.IsNullOrEmpty(existing.Title) && !_byTitle.ContainsKey(existing.Title))
                _byTitle.Add(existing.Title, existing);

            return existing;
        }

        public void Fixup()
        {
            var n = 0;
            foreach (var item in _byTitle.Values)
            {
                if (string.IsNullOrWhiteSpace(item.Id))
                {
                    var id = item.GetType().Name + "_g" + (++n);
                    _byId.Add(id, item);
                }
            }
        }
    }

    abstract class EntityInfo<T> : IEntityInfo<T>
        where T : EntityInfo<T>
    {
        public string Id { get; private set; }
        public string Title { get; private set; }

        protected void Populate(string id, string title)
        {
            if (!string.IsNullOrWhiteSpace(id))
            {
                if (id.ToLower().StartsWith("http://"))
                {
                    this.Id = id.Trim();
                }
                else
                {
                    this.Title = id.Trim();
                }
            }
            if (!string.IsNullOrWhiteSpace(title))
            {
                this.Title = title.Trim();
            }
        }

        public virtual void MergeFrom(T other)
        {
            if (string.IsNullOrEmpty(this.Id) && !string.IsNullOrEmpty(other.Id) && other.Id.ToLower().StartsWith("http://"))
                this.Id = other.Id;
            if (string.IsNullOrEmpty(this.Title) && !string.IsNullOrEmpty(other.Title))
                this.Title = other.Title;
        }

        public override string ToString()
        {
            return base.ToString() + $"[{this.Id}, {this.Title}]";
        }
    }

    class BookInfo : EntityInfo<BookInfo>
    {
        public string Isbn { get; private set; }
        public long? Pages { get; private set; }
        public string ReleaseYear { get; private set; }

        public HashSet<string> GenreId { get; private set; } = new HashSet<string>();
        public HashSet<string> ReleasePlaceId { get; private set; } = new HashSet<string>();
        public HashSet<string> AuthorId { get; private set; } = new HashSet<string>();

        public override void MergeFrom(BookInfo other)
        {
            this.GenreId.AddAll(other.GenreId);
            this.ReleasePlaceId.AddAll(other.ReleasePlaceId);
            this.AuthorId.AddAll(other.AuthorId);

            base.MergeFrom(other);
        }

        public static BookInfo Make(string id, string title, string isbn, string pages, string releaseDate, string releaseYear, string genreId, string releasePlaceId, string authorId)
        {
            var info = new BookInfo();
            info.Isbn = isbn;
            info.Pages = long.TryParse(pages, out var x) && x > 0 ? (long?)x : null;
            info.ReleaseYear = ObtainReleaseYear(releaseDate, releaseYear);
            if (!string.IsNullOrWhiteSpace(genreId))
                info.GenreId.Add(genreId);
            if (!string.IsNullOrWhiteSpace(releasePlaceId))
                info.ReleasePlaceId.Add(releasePlaceId);
            if (!string.IsNullOrWhiteSpace(authorId))
                info.AuthorId.Add(authorId);
            info.Populate(id, title);
            return info;
        }

        private static readonly Regex _yearRegex = new Regex(@"[\d]{4}");

        private static string ObtainReleaseYear(string releaseDate, string releaseYear)
        {
            var m2 = _yearRegex.Match(releaseYear);
            if (m2.Success)
                return m2.Value;

            var m1 = _yearRegex.Match(releaseDate);
            if (m1.Success)
                return m1.Value;

            return null;
        }
    }

    class GenreInfo : EntityInfo<GenreInfo>
    {
        public static GenreInfo Make(string id, string title)
        {
            var info = new GenreInfo();
            info.Populate(id, title);
            return info;
        }
    }

    class PlaceInfo : EntityInfo<PlaceInfo>
    {
        public static PlaceInfo Make(string id, string title)
        {
            var info = new PlaceInfo();
            info.Populate(id, title);
            return info;
        }
    }

    class AuthorInfo : EntityInfo<AuthorInfo>
    {
        public string BirthPlaceId { get; private set; }

        public override void MergeFrom(AuthorInfo other)
        {
            if (string.IsNullOrEmpty(this.BirthPlaceId) && !string.IsNullOrEmpty(other.BirthPlaceId))
                this.BirthPlaceId = other.BirthPlaceId;

            base.MergeFrom(other);
        }

        public static AuthorInfo Make(string id, string title, string birthPlaceId)
        {
            var info = new AuthorInfo();
            info.BirthPlaceId = birthPlaceId;
            info.Populate(id, title);
            return info;
        }
    }

    class DerivedMovieInfo : EntityInfo<DerivedMovieInfo>
    {
        public string BookId { get; private set; }

        public override void MergeFrom(DerivedMovieInfo other)
        {
            base.MergeFrom(other);
        }

        public static DerivedMovieInfo Make(string id, string title, string bookId)
        {
            var info = new DerivedMovieInfo();

            if (!string.IsNullOrWhiteSpace(bookId))
                info.BookId = bookId;

            info.Populate(id, title);
            return info;
        }
    }

    static class Program
    {
        const string allDataFileName = @"D:\ol\ol_dump_2022-03-29.txt\ol_dump_2022-03-29.txt";
        const string ratingsInfoFileName = @"D:\ol\ol_dump_ratings_2022-03-29.txt";

        static void Main(string[] args)
        {
            var owl = new XmlDocument();
            var srcFile = @"D:\projects\owl\OwlBooks\MyBooksOWL.owl";
            var dstFile = @"D:\projects\owl\OwlBooks\MyBooksOWL-out.owl";
            owl.Load(srcFile);

            var entities = new Dictionary<string, XmlElement>();
            foreach (var el in owl.SelectNodes(@"/*[local-name()='RDF']/*[local-name()='NamedIndividual']").OfType<XmlElement>())
            {
                entities.Add(el.GetAttribute("about", xmlns.rdf), el);
            }

            var ratings = ReadRatings();

            Thread.CurrentThread.CurrentCulture = System.Globalization.CultureInfo.InvariantCulture;
            Thread.CurrentThread.CurrentUICulture = System.Globalization.CultureInfo.InvariantCulture;

            var books = new EntityRegistry<BookInfo>();
            var places = new EntityRegistry<PlaceInfo>();
            var authors = new EntityRegistry<AuthorInfo>();
            var movies = new EntityRegistry<DerivedMovieInfo>();
            var genres = new EntityRegistry<GenreInfo>();

            var data = ReadFileLines(@"D:\ol\sparql_last_2022-05-22_23-22-46Z.tsv", n => { }).Select((line, n) => {
                if (n == 0)
                    return null;

                var parts = line.Split(new[] { "\t" }, StringSplitOptions.None).Select(s => s.Trim('"')).ToArray();

                var bookId = parts.ItemOrDefault(0);
                var isbn = parts.ItemOrDefault(1).Replace("-", "");
                var bookTitle = parts.ItemOrDefault(2);
                var pages = parts.ItemOrDefault(3);
                var bookReleaseDate = parts.ItemOrDefault(4);
                var bookReleaseYear = parts.ItemOrDefault(5);
                var bookGenreId = parts.ItemOrDefault(6);
                var bookGenreTitle = parts.ItemOrDefault(7);
                var bookCountryId = parts.ItemOrDefault(8);
                var bookCountryTitle = parts.ItemOrDefault(9);
                var authorId = parts.ItemOrDefault(10);
                var authorLabel = parts.ItemOrDefault(11);
                var authorBirthDate = parts.ItemOrDefault(12);
                var authorBirthPlaceId = parts.ItemOrDefault(13);
                var authorBirthPlaceLabel = parts.ItemOrDefault(14);
                var movieId = parts.ItemOrDefault(15);
                var movieTitle = parts.ItemOrDefault(16);

                if (parts.Length < 13)
                    Console.WriteLine("Invalid row " + n);

                return new {
                    rowNum = n,
                    bookId,
                    isbn,
                    bookTitle,
                    pages,
                    bookReleaseDate,
                    bookReleaseYear,
                    bookGenreId,
                    bookGenreTitle,
                    bookCountryId,
                    bookCountryTitle,
                    authorId,
                    authorLabel,
                    authorBirthDate,
                    authorBirthPlaceId,
                    authorBirthPlaceLabel,
                    movieId,
                    movieTitle
                };
            }).Where(l => l != null).ToList();

            foreach (var item in data)
            {
                places.Resolve(PlaceInfo.Make(item.bookCountryId, item.bookCountryTitle));
                places.Resolve(PlaceInfo.Make(item.authorBirthPlaceId, item.authorBirthPlaceLabel));
                genres.Resolve(GenreInfo.Make(item.bookGenreId, item.bookGenreTitle));
            }

            places.Fixup();
            genres.Fixup();

            foreach (var item in data)
            {
                var authorBirthCountry = places.Resolve(PlaceInfo.Make(item.authorBirthPlaceId, item.authorBirthPlaceLabel));
                authors.Resolve(AuthorInfo.Make(item.authorId, item.authorLabel, authorBirthCountry?.Id));
            }

            authors.Fixup();

            foreach (var item in data)
            {
                var bookCountry = places.Resolve(PlaceInfo.Make(item.bookCountryId, item.bookCountryTitle));
                var authorBirtCountry = places.Resolve(PlaceInfo.Make(item.authorBirthPlaceId, item.authorBirthPlaceLabel));
                var genre = genres.Resolve(GenreInfo.Make(item.bookGenreId, item.bookGenreTitle));
                var author = authors.Resolve(AuthorInfo.Make(item.authorId, item.authorLabel, authorBirtCountry?.Id));

                books.Resolve(BookInfo.Make(item.bookId, item.bookTitle, item.isbn, item.pages, item.bookReleaseDate, item.bookReleaseYear, genre?.Id, bookCountry?.Id, author?.Id));
            }

            foreach (var item in data) 
            {
                movies.Resolve(DerivedMovieInfo.Make(item.movieId, item.movieTitle, item.bookId));
            }

            movies.Fixup();


            //var bookId = "http://www.semanticweb.org/e1izabeth/ontobooks#bookByIsbn:" + isbn;
            //var derivedId = "http://www.semanticweb.org/e1izabeth/ontobooks#filmsByBookIsbn:" + isbn;

            foreach (var place in places.GetEntities())
            {
                owl.DocumentElement.Append(XmElement(
                    xmlns.owl, "NamedIndividual", null,
                    XmAttribute(xmlns.rdf, "about", place.Id),
                    XmElement(xmlns.rdf, "type", null, XmAttribute(xmlns.rdf, "resource", "http://www.semanticweb.org/e1izabeth/ontobooks#Country")),
                    XmElement(xmlns.rdfs, "label", place.Title)
                ));
            }
            foreach (var genre in genres.GetEntities())
            {
                owl.DocumentElement.Append(XmElement(
                    xmlns.owl, "NamedIndividual", null,
                    XmAttribute(xmlns.rdf, "about", genre.Id),
                    XmElement(xmlns.rdf, "type", null, XmAttribute(xmlns.rdf, "resource", "http://www.semanticweb.org/e1izabeth/ontobooks#Genre")),
                    XmElement(xmlns.rdfs, "label", genre.Title)
                ));
            }
            foreach (var author in authors.GetEntities())
            {
                owl.DocumentElement.Append(XmElement(
                    xmlns.owl, "NamedIndividual", null,
                    XmAttribute(xmlns.rdf, "about", author.Id),
                    XmElement(xmlns.rdf, "type", null, XmAttribute(xmlns.rdf, "resource", "http://www.semanticweb.org/e1izabeth/ontobooks#Author")),
                    XmElement(xmlns.rdfs, "label", author.Title),
                    XmIfAny(author.BirthPlaceId, id => XmElement(xmlns.ontobooks, "origin", null, XmAttribute(xmlns.rdf, "resource", id)))
                ));
            }
            foreach (var book in books.GetEntities())
            {
                owl.DocumentElement.Append(XmElement(
                    xmlns.owl, "NamedIndividual", null,
                    XmAttribute(xmlns.rdf, "about", book.Id),
                    XmElement(xmlns.rdf, "type", null, XmAttribute(xmlns.rdf, "resource", "http://www.semanticweb.org/e1izabeth/ontobooks#Books")),
                    XmElement(xmlns.rdfs, "label", book.Title),
                    XmElements(book.ReleasePlaceId.Select(id => XmElement(xmlns.ontobooks, "origin", null, XmAttribute(xmlns.rdf, "resource", id)))),
                    XmElements(book.GenreId.Select(id => XmElement(xmlns.ontobooks, "hasGenre", null, XmAttribute(xmlns.rdf, "resource", id)))),
                    XmElements(book.AuthorId.Select(id => XmElement(xmlns.ontobooks, "hasAuthoredBy", null, XmAttribute(xmlns.rdf, "resource", id)))),
                    XmIfAnyValue(ratings.TryGetValue(book.Isbn, out var v) ? v : NoValue<double>(), x => XmElement(xmlns.ontobooks, "hasRating", $"{x:00.00}", XmAttribute(xmlns.rdf, "datatype", "http://www.w3.org/2001/XMLSchema#float"))),
                    XmIfAny(book.Pages?.ToString() ?? null, s => XmElement(xmlns.ontobooks, "hasNoOfPages", s, XmAttribute(xmlns.rdf, "datatype", "http://www.w3.org/2001/XMLSchema#integer"))),
                    XmIfAny(book.ReleaseYear, s => XmElement(xmlns.ontobooks, "hasPublishedYear", s, XmAttribute(xmlns.rdf, "datatype", "http://www.w3.org/2001/XMLSchema#integer"))),
                    XmElement(xmlns.ontobooks, "hasTitle", book.Title, XmAttribute(xmlns.rdf, "datatype", "http://www.w3.org/2001/XMLSchema#string"))
                ));
            }
            foreach (var movie in movies.GetEntities())
            {
                owl.DocumentElement.Append(XmElement(
                    xmlns.owl, "NamedIndividual", null,
                    XmAttribute(xmlns.rdf, "about", movie.Id),
                    XmElement(xmlns.rdf, "type", null, XmAttribute(xmlns.rdf, "resource", "http://www.semanticweb.org/e1izabeth/ontobooks#Film")),
                    XmElement(xmlns.rdfs, "label", movie.Title),
                    XmElement(xmlns.ontobooks, "isBasedOnBook", null, XmAttribute(xmlns.rdf, "resource", movie.BookId)),
                    XmElement(xmlns.ontobooks, "hasTitle", movie.Title, XmAttribute(xmlns.rdf, "datatype", "http://www.w3.org/2001/XMLSchema#string"))
                ));
            }

            //owl.DocumentElement.Append(XmElement(
            //    xmlns.owl, "NamedIndividual", null,
            //    XmAttribute(xmlns.rdf, "about", bookId),
            //    XmElement(xmlns.rdf, "type", null, XmAttribute(xmlns.rdf, "resource", "http://www.semanticweb.org/e1izabeth/ontobooks#Books")),
            //    XmElement(xmlns.rdfs, "label", bookTitle),
            //    XmElement(xmlns.ontobooks, "hasGenre", null, XmAttribute(xmlns.rdf, "resource", "http://www.semanticweb.org/e1izabeth/ontobooks#Crime")),
            //    XmElement(xmlns.ontobooks, "hasGenre", null, XmAttribute(xmlns.rdf, "resource", "http://www.semanticweb.org/e1izabeth/ontobooks#Fiction")),
            //    XmElement(xmlns.ontobooks, "hasGenre", null, XmAttribute(xmlns.rdf, "resource", "http://www.semanticweb.org/e1izabeth/ontobooks#Thriller")),
            //    XmIfAnyValue(ratings.TryGetValue(isbn, out var v) ? v : NoValue<double>(), x => XmElement(xmlns.ontobooks, "hasRating", $"{x:00.00}", XmAttribute(xmlns.rdf, "datatype", "http://www.w3.org/2001/XMLSchema#float"))),
            //    XmElement(xmlns.ontobooks, "hasNoOfPages", "12345", XmAttribute(xmlns.rdf, "datatype", "http://www.w3.org/2001/XMLSchema#integer"))
            //));
            //owl.DocumentElement.Append(XmElement(
            //    xmlns.owl, "NamedIndividual", null,
            //    XmAttribute(xmlns.rdf, "about", derivedId),
            //    XmElement(xmlns.rdf, "type", null, XmAttribute(xmlns.rdf, "resource", "http://www.semanticweb.org/e1izabeth/ontobooks#Film")),
            //    XmElement(xmlns.rdfs, "label", derivedTitle),
            //    XmElement(xmlns.ontobooks, "isBasedOnBook", null, XmAttribute(xmlns.rdf, "resource", bookId))
            //));

            owl.Save(dstFile);
        }

        static T? NoValue<T>()
            where T : struct
        {
            return default;
        }

        static XmlElement Append(this XmlElement element, XmlElementModel childModel)
        {
            var childElt = element.AddElement(childModel.ns, childModel.name, childModel.content);
            foreach (var item in childModel.children)
            {
                item.Apply(XmlModelMaterializer.Instance, childElt);
            }
            return childElt;
        }

        static XmlNodeModel XmIf(bool cond, Func<XmlNodeModel> src)
        {
            return cond ? src() : XmlNothingModel.Instance;
        }

        static XmlNodeModel XmIfAny<T>(T value, Func<T, XmlNodeModel> src)
            where T : class
        {
            return value != null ? src(value) : XmlNothingModel.Instance;
        }

        static XmlNodeModel XmIfAnyValue<T>(T? value, Func<T, XmlNodeModel> src)
            where T : struct
        {
            return value.HasValue ? src(value.Value) : XmlNothingModel.Instance;
        }

        static XmlAttrModel XmAttribute(string ns, string name, string value)
        {
            return new XmlAttrModel(ns, name, value);
        }

        static XmlElementModel XmElement(string ns, string name, string content, params XmlNodeModel[] children)
        {
            return new XmlElementModel(ns, name, content, new ReadOnlyCollection<XmlNodeModel>(children));
        }

        static XmlElementsModel XmElements(IEnumerable<XmlNodeModel> children)
        {
            return new XmlElementsModel(new ReadOnlyCollection<XmlNodeModel>(children.ToList()));
        }

        class XmlModelMaterializer : IXmlNodeModelVisitor<XmlNode, XmlElement>
        {
            public static readonly XmlModelMaterializer Instance = new XmlModelMaterializer();

            private XmlModelMaterializer() { }

            XmlNode IXmlNodeModelVisitor<XmlNode, XmlElement>.VisitAttrModel(XmlAttrModel attr, XmlElement arg)
            {
                arg.SetAttribute(attr.name, attr.ns, attr.value);
                return null;
            }

            XmlNode IXmlNodeModelVisitor<XmlNode, XmlElement>.VisitElementModel(XmlElementModel elt, XmlElement arg)
            {
                return arg.Append(elt);
            }

            XmlNode IXmlNodeModelVisitor<XmlNode, XmlElement>.VisitElementsModel(XmlElementsModel elts, XmlElement arg)
            {
                foreach (var elt in elts.children)
                    elt.Apply(this, arg);
                return null;
            }

            XmlNode IXmlNodeModelVisitor<XmlNode, XmlElement>.VisitNothingModel(XmlNothingModel nothing, XmlElement arg)
            {
                return null;
            }
        }

        interface IXmlNodeModelVisitor<T, TArg>
        {
            T VisitElementModel(XmlElementModel elt, TArg arg);
            T VisitAttrModel(XmlAttrModel attr, TArg arg);
            T VisitNothingModel(XmlNothingModel nothing, TArg arg);
            T VisitElementsModel(XmlElementsModel elts, TArg arg);
        }
        abstract class XmlNodeModel
        {
            public abstract T Apply<T, TArg>(IXmlNodeModelVisitor<T, TArg> visitor, TArg arg);
        }
        class XmlElementsModel : XmlNodeModel
        {
            public readonly ReadOnlyCollection<XmlNodeModel> children;

            public XmlElementsModel(ReadOnlyCollection<XmlNodeModel> children)
            {
                this.children = children;
            }

            public override T Apply<T, TArg>(IXmlNodeModelVisitor<T, TArg> visitor, TArg arg)
            {
                return visitor.VisitElementsModel(this, arg);
            }
        }
        class XmlElementModel : XmlNodeModel
        {
            public readonly string ns, name, content;
            public readonly ReadOnlyCollection<XmlNodeModel> children;

            public XmlElementModel(string ns, string name, string content, ReadOnlyCollection<XmlNodeModel> children)
            {
                this.ns = ns;
                this.name = name;
                this.content = content;
                this.children = children;
            }

            public override T Apply<T, TArg>(IXmlNodeModelVisitor<T, TArg> visitor, TArg arg)
            {
                return visitor.VisitElementModel(this, arg);
            }
        }
        class XmlAttrModel : XmlNodeModel
        {
            public readonly string ns, name, value;

            public XmlAttrModel(string ns, string name, string value)
            {
                this.ns = ns;
                this.name = name;
                this.value = value;
            }

            public override T Apply<T, TArg>(IXmlNodeModelVisitor<T, TArg> visitor, TArg arg)
            {
                return visitor.VisitAttrModel(this, arg);
            }
        }
        class XmlNothingModel : XmlNodeModel
        {
            public static readonly XmlNothingModel Instance = new XmlNothingModel();

            private XmlNothingModel() { }

            public override T Apply<T, TArg>(IXmlNodeModelVisitor<T, TArg> visitor, TArg arg)
            {
                return visitor.VisitNothingModel(this, arg);
            }
        }

        private static XmlElement AddElement(this XmlElement element, string ns, string name, string content = null)
        {
            var elt = element.OwnerDocument.CreateElement(name, ns);
            element.AppendChild(elt);

            if (content != null)
            {
                elt.InnerText = content;
            }

            return elt;
        }

        static T ItemOrDefault<T>(this T[] arr, int index)
        {
            return arr.Length > index ? arr[index] : default(T);
        }

        static Dictionary<string, double> ReadRatings()
        {
            var ratingsByIsbn = new Dictionary<string, double>();
            foreach (var line in ReadFileLines(@"D:\ol\byWorkRatings.txt", n => Console.WriteLine(n)))
            {
                var parts = line.Split(new[] { "\t" }, StringSplitOptions.None);
                var workId = parts[0];
                var bookId = parts[1];
                var rating = double.Parse(parts[2]);

                foreach (var isbn in parts[3].Trim('[', ']').Split(',').Select(s => s.Trim()))
                {
                    ratingsByIsbn[isbn] = rating;
                }
            }

            return ratingsByIsbn;
        }

        static void CheckRatingsByIsbn()
        {
            var isbns = new[]{
                "1-56512-217-8","978-0-7636-4410-9","978-0-553-21277-8","978-0-674-00078-0","978-0-679-73577-9",
                "0-440-08721-X","978-0-571-15310-7","9780062658753","978-0-14-015754-3","0-446-52080-2","978-0-14-001783-0",
                "9780140186390","0-575-05748-3","0-06-039144-8","0-394-80497-X","0-207-14366-8","978-0-446-36538-3",
                "0-06-113937-8","978-0-385-08695-0","978-1840243536","978-0450044496","0-15-119153-0","0-618-47794-2",
                "0-670-88072-8","0-446-51652-X","0-9512072-0-2","0-385-50069-6","0-670-68686-7","0-00-727903-5","0-394-80079-6",
                "0-593-04510-6","0-413-50890-0","0-394-82337-0","0-554-31409-6","0-7868-5629-7","0-517-55951-X","9780854681877",
                "0-224-60578-X","0-7434-5150-3","0-06-054209-8","978-0-525-94525-3","0-394-46901-1","0-14-118069-2","0-330-35293-8",
                "0-679-74472-X","0-448-16538-4","978-1-59420-009-0","978-0-75964-018-4","0-786-80995-7",
                "0-14-037355-1","978-0-14-013727-9","978-0-374-36877-7","978-1-61213-028-6"
            };

            var ratingsByIsbn = ReadRatings();

            Console.WriteLine();
            var c = 0;
            foreach (var isbn in isbns)
            {
                if (ratingsByIsbn.TryGetValue(isbn.Replace("-", ""), out var rating))
                {
                    c++;
                    Console.WriteLine($"{isbn} \t {rating}");
                }
            }
            Console.WriteLine($"{c}/{isbns.Length}");
        }

        static void CollectRatingsByIsbn()
        {
            Console.WriteLine("Reading ratings");
            var rr = CollectRatings(x => Console.WriteLine(x));
            rr.SaveTo("byWorkRatings.txt", "byBookRatings.txt");


            Console.WriteLine("Reading data");
            var booksCovered = 0;
            var worksCovered = 0;
            var genreStrings = new Dictionary<string, string>();
            string internGenreString(string s)
            {
                if (genreStrings.TryGetValue(s, out var result))
                {
                    return result;
                }
                else
                {
                    genreStrings.Add(s, s);
                    return s;
                }
            }
            foreach (var line in ReadFileLines(allDataFileName, x => Console.WriteLine($"{x}\t| {booksCovered}/{rr.BooksCount}, {worksCovered}/{rr.WorksCount}")))
            {
                /*
type - type of record (/type/edition, /type/work etc.)
key - unique key of the record. (/books/OL1M etc.)
revision - revision number of the record
last_modified - last modified timestamp
JSON - the complete record in JSON format
                */
                var parts = line.Split(new[] { '\t' });
                var typeKey = parts[0];
                var entityKey = parts[1];
                var entityJson = parts[4];
                if (typeKey == KnownTypeKeys.edition)
                {
                    try
                    {
                        var bookInfo = Json.Book.QuickType.BookInfo.FromJson(entityJson);
                        // bookInfo.Genres
                        if (rr.TryGetByBookId(bookInfo.Key, out var br))
                        {
                            booksCovered++;
                            if (bookInfo.Isbn10 != null)
                                br.Isbn.AddAll(bookInfo.Isbn10);
                            if (bookInfo.Isbn13 != null)
                                br.Isbn.AddAll(bookInfo.Isbn13);
                            if (bookInfo.Genres != null)
                                br.Genres.AddAll(bookInfo.Genres.Select(internGenreString));
                        }
                        if (bookInfo.Works != null)
                        {
                            worksCovered++;
                            foreach (var workRef in bookInfo.Works)
                            {
                                if (rr.TryGetByWorkId(workRef.Key, out var wr))
                                {
                                    if (bookInfo.Isbn10 != null)
                                        wr.Isbn.AddAll(bookInfo.Isbn10);
                                    if (bookInfo.Isbn13 != null)
                                        wr.Isbn.AddAll(bookInfo.Isbn13);
                                    if (bookInfo.Genres != null)
                                        wr.Genres.AddAll(bookInfo.Genres.Select(internGenreString));
                                }
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(entityJson);
                        Console.WriteLine(ex);
                        Console.ReadLine();
                    }
                }
            }


            Console.WriteLine();
        }

        static void CollectTypes()
        {
            var types = new HashSet<string>();
            foreach (var line in ReadFileLines(allDataFileName, x => Console.WriteLine(x)))
            {
                /*
/type/author
/type/redirect
/type/delete
/type/edition
/type/page
/type/i18n
/type/language
/type/library
/type/subject
/type/template
/type/work
/type/macro
/type/type
/type/rawtext
/type/volume
/type/object
/type/backreference
/type/about
/type/home
/type/local_id
/type/permission
/type/i18n_page
/type/series
/type/user
/type/usergroup
/type/collection
/type/scan_record
/type/doc
/type/uri
/type/place
/type/scan_location

type - type of record (/type/edition, /type/work etc.)
key - unique key of the record. (/books/OL1M etc.)
revision - revision number of the record
last_modified - last modified timestamp
JSON - the complete record in JSON format
                */
                var parts = line.Split(new[] { '\t' });

                types.Add(parts[0]);
            }

            foreach (var t in types)
            {
                Console.WriteLine(t);
            }

        }

        static RatingRegistry CollectRatings(Action<double> progressHandler)
        {
            var registry = new RatingRegistry();
            foreach (var line in ReadFileLines(ratingsInfoFileName, progressHandler))
            {
                // "Work Key, Edition Key (optional), Rating, Date"
                var parts = line.Split(new[] { '\t' }, StringSplitOptions.None);
                registry.Add(parts[0], parts[1], int.Parse(parts[2]));
            }

            return registry;
        }

        static IEnumerable<string> ReadFileLines(string fileName, Action<double> progressHandler)
        {
            var types = new HashSet<string>();
            var inputFile = new FileInfo(fileName);
            long n = 0, len = inputFile.Length;
            using (var input = inputFile.OpenText())
            {
                while (!input.EndOfStream)
                {
                    var line = input.ReadLine();
                    if (line != null)
                    {
                        line = line.Trim();
                        if (line.Length > 0)
                        {
                            yield return line;
                        }
                    }

                    if (n % 1000 == 0)
                    {
                        progressHandler(input.BaseStream.Position * 100.0 / len);
                    }
                    n++;
                }
            }
        }

        public static void AddAll<T>(this ICollection<T> collection, IEnumerable<T> source)
        {
            foreach (var item in source)
            {
                collection.Add(item);
            }
        }
    }


}
