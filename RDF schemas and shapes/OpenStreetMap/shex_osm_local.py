from shexer.shaper import Shaper, ALL_EXAMPLES, TURTLE_ITER
namespaces_dict = {
   "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
   "http://example.org/": "ex",
   "http://weso.es/shapes/": "shape",
   "http://www.w3.org/2001/XMLSchema#": "xsd",
   "http://www.w3.org/2002/07/owl#": "owl",
   "https://biodatafuse.org/example/" : "graph",
   "http://purl.obolibrary.org/obo/": "obo",
}

graph_path = "nld.osm.ttl"

shaper = Shaper(
   all_classes_mode=True,
   examples_mode=ALL_EXAMPLES,
   graph_file_input=graph_path,
   input_format=TURTLE_ITER,
   namespaces_dict=namespaces_dict,
   disable_or_statements=False,
   instances_cap=10000
)


shaper.shex_graph(output_file="osm_sample_10000.shex",
                               acceptance_threshold=0,
                               verbose=True)
print("Done")
