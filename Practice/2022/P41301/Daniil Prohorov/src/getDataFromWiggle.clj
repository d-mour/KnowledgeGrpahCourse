(ns test.core)
(use 'hickory.core)
(require '[clj-http.client :as client])
(require '[hickory.select :as s])
(require '[clojure.string :as str])
(require '[clojure.core.match :refer [match]])
(require '[clojure.data.json :as json])
(use '[clojure.string :only (join split)])
(use 'overtone.at-at)

(doseq [arg *command-line-args*]
  (printf "arg='%s'\n" arg))

(defn -main [arg]
  (printf "arg='%s'\n" arg))

(defn urlConcat
  [prefix postfix]
  (str/join "/" [prefix postfix]))

(def startUrl "https://www.wiggle.co.uk/cycle/bike-parts")
(def filterUrlsBase
  ["https://www.wiggle.co.uk/"])

(def cycleUrlBase "https://www.wiggle.co.uk/cycle")

(defn foo
  "I don't do a whole lot."
  [x]
  (println x "Hello, World!"))

(defn getHtml
  [url]
  (-> (client/get url) :body parse as-hickory
      ))

(def wigglePrefix
  "https://www.wiggle.co.uk/cycle/")

(defn getCategoriesUrls
  ([url]
   (getCategoriesUrls url filterUrlsBase))
  ([url filterUrls]
   (let
     [html (getHtml url)
      lst (-> (s/select
                (s/class "plp-refinements__section__list__item-link")
                html))
      urls (map #((% :attrs) :href) lst)
      urlModification (comp #(str/replace % wigglePrefix "") #(str/replace % "#breadcrumbs" ""))
      urlsWithoutBreadcrumbs (map urlModification urls)
      base (str/replace url wigglePrefix "")
      filterUrls_ (conj filterUrls url)
      filtered (remove (set (map urlModification filterUrls_)) urlsWithoutBreadcrumbs)
      ]
     {:base base :urls filtered :filterUrls filterUrls_}
     ;filterUrls_
     ;urlsWithoutBreadcrumbs
     ))
  )

(defn getAllLinks [arg]
  (match arg
         {:base base :urls urls :filterUrls filterUrls}
         (let [links (map #(getCategoriesUrls (urlConcat cycleUrlBase %) filterUrls) urls)
               next_val (map getAllLinks links)
               ]
           {(keyword base) (into (hash-map) next_val)}
           )
         ;urls
         {:base base :urls [] :filterUrls filterUrls}
         base
         :else
         :no-match))


(def structure
  {:bike-parts {:seating              {:saddles             {},
                                       :seat-posts          {},
                                       :dropper-seats-posts {},
                                       :seat-post-clamps    {},
                                       :seat-post-spares    {},
                                       :dropper-remotes     {},
                                       :saddle-care-kits    {}},
                :cleats-and-spares    {:cleats {}, :cleat-covers {}},
                :power-meters         {:power-meter-chainsets {}, :power-meter-cranksets {}, :power-meter-pedals {}},
                :frames               {:road-bike-frames       {},
                                       :mountain-bike-frames   {:hard-tail-mountain-bike-frames {}, :full-sus-mountain-bike-frames {}},
                                       :cyclocross-bike-frames {},
                                       :adventure-bike-frames  {},
                                       :time-trial-bike-frames {},
                                       :bmx-bike-frames        {},
                                       :electric-bike-frames   {},
                                       :kids-bike-frames       {}},
                :brakes               {:brake-levers            {},
                                       :brake-hose              {},
                                       :rim-brake-pads          {},
                                       :disc-brake-pads         {},
                                       :brake-spares            {},
                                       :brake-bleed-kits        {},
                                       :disc-brake-rotors       {},
                                       :rim-brakes              {},
                                       :brake-cables-and-spares {:brake-cables {}, :brake-cables-spares {}},
                                       :brake-oils              {},
                                       :disc-brake-callipers-1  {}},
                :drivetrain-and-gears {:bash-guards                  {},
                                       :groupsets                    {},
                                       :front-derailleurs-and-spares {},
                                       :chainsets                    {},
                                       :gear-levers-and-spares       {:gear-levers {}, :gear-lever-spares {}},
                                       :bottom-brackets-and-spares   {:bottom-brackets {}, :bottom-bracket-spares {}},
                                       :mech-hangers                 {},
                                       :chain-rings                  {},
                                       :cassettes-and-spares         {:cassettes {}, :cassette-spares {}},
                                       :rear-derailleurs-and-spares  {:rear-derailleurs       {},
                                                                      :jockey-wheels          {},
                                                                      :rear-derailleur-spares {}},
                                       :gear-cables-and-spares       {:gear-cables {}, :gear-cable-spares {}},
                                       :chains-and-spares            {:chains {}, :chain-links {}},
                                       :electronic-gear-spares       {},
                                       :cranksets                    {},
                                       :freehubs-and-spares          {:freehubs {}, :freehub-spares {}}},
                :steering             {:handlebars          {:drop-handlebars     {},
                                                             :riser-handlebars    {},
                                                             :flat-handlebars     {},
                                                             :aero-bars           {},
                                                             :tt-handlebars       {},
                                                             :bullhorn-handlebars {},
                                                             :handlebar-spares    {}},
                                       :bar-tape            {},
                                       :bar-grips           {},
                                       :bar-ends            {},
                                       :bar-plugs           {},
                                       :headsets-and-spares {:headsets {}, :headset-spacers {}, :top-caps {}},
                                       :stems-and-spares    {:stems {}, :stem-spares {}}},
                :forks                {:rigid-forks               {},
                                       :suspension-and-spares     {:suspension-forks {}, :rear-shocks {}, :suspension-fork-spares {}},
                                       :suspension-tuning-systems {}},
                :pedals-and-spares    {:pedals {:clip-in-pedals {}, :flat-pedals {}}, :pedal-spares {}}}}
  )

(defn linksGroupsCreate
  ([]
   (let
     [url (urlConcat cycleUrlBase "bike-parts")
      ]
     (linksGroupsCreate url (structure :bike-parts))
     ))
  ([keyNames_ struct]
   (let
     [keyNames (map name (keys struct))
      ;;urls (map #(urlConcat urlBase %) keyNames)
      ]
     ;(linksCreate url (structure :bike-parts))
     (if
       (empty? struct)
       (map #(urlConcat cycleUrlBase %1) keyNames_)
       ;;(mapcat #(linksGroupsCreate %1 (struct %2)) urls (keys struct))
       (mapcat #(linksGroupsCreate keyNames (struct %1)) (keys struct))
       )
     )
   )
  )

(def linksGroups (distinct (linksGroupsCreate)))

(def my-pool (mk-pool))

(defn doseq-interval
  [f coll interval]
  (doseq [x coll]
    (Thread/sleep interval)
    (f x)))


(defn getLinksFromPage
  [url]
  (let
    [html (getHtml url)
     items (-> (s/select
                 (s/class "bem-product-thumb__image-link--grid")
                 html))
     paginator (-> (s/select
                     (s/class "bem-paginator__link")
                     html))
     nextUrl (first (filter #(= (% :content) [">"]) paginator))
     urls (map #((% :attrs) :href) items)
     ;delay (reduce + (filter odd? (map inc (range 130000000))))
     ]
    ;;(if
    ;;  (or (nil? nextUrl) (> (count items) 40 ))
    ;;  urls
    ;;  (mapcat urls (getLinksFromPage ((nextUrl :attrs) :href)))
    ;;)
    ;;(if
    ;;  (nil? nextUrl)
    ;;  take 5 urls
    ;;  (concat urls (getLinksFromPage ((nextUrl :attrs) :href)))
    ;;)
    (take 2 urls)
    )
  )

(def links
  (mapcat getLinksFromPage linksGroups))

(defn filterString
  [str]
  (if (empty? str)
    str
    (let
      [prefilter (str/replace str #"\r\n" "")
       splited (split prefilter #" ")
       filtered (filter #(not= "" %) splited)
       joined (join " " filtered)
       ]
      joined
      )
    )
  )

(defn getItemsDescription
  [url]
  (let
    [html (getHtml url)
     titleHtml (-> (s/select
                     (s/id "productTitle")
                     html))
     topFeaturesHtml (-> (s/select
                           (s/class "bem-pdp__features-item")
                           html))
     priceHtml (-> (s/select
                     (s/class "bem-pricing__product-price")
                     html))

     topFeatures (map #(first (% :content)) topFeaturesHtml)
     title (first ((first titleHtml) :content))
     price (((first priceHtml) :attrs) :data-default-value)
     ]
    {:title       (filterString title)
     :topFeatures (map filterString topFeatures)
     :price       price
     :url url
     }
    )
  )




