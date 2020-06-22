# QUERIES
study_types = ('SELECT ?study_types\n'
               'WHERE {?study_types rdfs:subClassOf :StudyType}')

annotations = ('SELECT ?annotations\n'
               'WHERE {?annotations rdfs:subClassOf :Annotation}')

internal_organs = ('SELECT ?internal_organs\n'
                   'WHERE {?internal_organs rdf:type :InternalOrgans}')

part_of_body = ('SELECT ?part_of_body\n'
                'WHERE {?part_of_body rdf:type :PartOfBody}')

annotated_scans = ('SELECT ?annotated_scans\n'
                   'WHERE {?annotated_scans rdf:type :Annotated}')

not_annotated_scans = ('SELECT ?annotated_scans\n'
                       'WHERE {?annotated_scans rdf:type :NotAnnotated}')

localizer_scans = ('SELECT ?localizer_scans\n'
                   'WHERE {?localizer_scans rdf:type :Localizer}')

general_scans = ('SELECT ?general_scans\n'
                 'WHERE {?general_scans rdf:type :General}')

images_with_head = ('SELECT ?images_with_head\n'
                    'WHERE {?images_with_head :has_LS_Annotation :Head}')

images_with_neck = ('SELECT ?images_with_neck\n'
                    'WHERE {?images_with_neck :has_LS_Annotation :Neck}')

images_with_chest = ('SELECT ?images_with_chest\n'
                     'WHERE {?images_with_chest :has_LS_Annotation :Chest}')

images_with_abdomen = ('SELECT ?images_with_abdomen\n'
                       'WHERE {?images_with_abdomen :has_LS_Annotation :Abdomen}')

images_with_pelvis = ('SELECT ?images_with_pelvis\n'
                      'WHERE {?images_with_pelvis :has_LS_Annotation :Pelvis}')
