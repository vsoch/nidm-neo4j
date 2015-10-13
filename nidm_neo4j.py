from nidmviewer.convert import get_lookups, get_nidm_keys, get_field_groups
from nidmviewer.convert import getjson
from rdflib.serializer import Serializer
from rdflib import Graph as graphrdf, plugin
import rdfextras
rdfextras.registerplugins()
plugin.register(
    'json-ld',
    Serializer,
    'rdflib_jsonld.serializer',
    'JsonLDSerializer')
import numpy
import json
import re
import os
import sys

ttl_file = sys.argv[1]
outfolder = sys.argv[2]
username = sys.argv[3]
repo_name = sys.argv[4]

if not os.path.exists(outfolder):
    os.mkdir(outfolder)

ttl = getjson(ttl_file)

# create a node
def create_node(nid,node_type,uid,name,properties):
    node_type = node_type.lower().replace(" ","").replace("'","").replace("-","")
    name = name.replace("'","").replace("-","")
    if len(properties) > 0:
        property_string = ""
        for p in range(len(properties)):
            property_name = properties[p][0].lower().replace(" ","").replace("'","").replace("-","")
            property_value = properties[p][1]
            property_string = "%s %s : '%s'," %(property_string,property_name,property_value)
        property_string = property_string[:-1]
        return "create (_%s:%s { id : '%s', name :'%s', %s})\n" %(nid,node_type,uid,name,property_string)
    else:
        return "create (_%s:%s { id : '%s', name :'%s'})\n" %(nid,node_type,uid,name)

# create a relationship
def create_relation(nid1,nid2,relationship):
    relationship = relationship.upper().replace("'","").replace("-","")
    return "create _%s-[:'%s']->_%s\n" %(nid1,relationship,nid2)

fields,lookup = get_lookups(ttl)
groups = get_field_groups(ttl)
manual_fields = get_nidm_keys()
for name,uri in manual_fields.iteritems():
    if uri not in lookup:
        lookup[uri] = name

# First we will save data structures to look up node ids based on URI
nodes = dict()

count = 1
for result in ttl:
    rgroup = [x for x in result["@type"] if x in groups][0] 
    rtype = [x for x in result["@type"] if x != rgroup]
    if len(rtype)>0:
        rtype = rtype[0]
        if rtype in lookup.keys():
            result_id = result["@id"].encode("utf-8")
            if result_id not in nodes:
                nodes[result_id] = count
                count +=1

# Define ids of relationships

labeluri = "http://www.w3.org/2000/01/rdf-schema#label"

relations = list()
neo4j = list()

for result in ttl:
    rgroup = [x for x in result["@type"] if x in groups][0] 
    rtype = [x for x in result["@type"] if x != rgroup]
    if len(rtype)>0:
        rtype = rtype[0]
        if rtype in lookup.keys():
            node_id = nodes[result_id] # Here is the node_id
            result_id = result["@id"]
            label = lookup[rtype]
            if labeluri in result:
                name = result[labeluri][0]["@value"].encode("utf-8")
            else:
                name = "%s_%s" %(label,count)
            # Find things we know about
            data = [x for x in result.keys() if x in lookup.keys()]
            data_labels = [lookup[d] for d in data]
            # We will save a list of properties and values for the node
            properties = []
            for d in range(len(data)):
                datum = data[d]
                human_label = data_labels[d]
                # If it just has an id, assume it's a relationship
                if "@id" in result[datum][0].keys():
                    if result[datum][0]["@id"] in nodes:
                        relation_id = nodes[result[datum][0]["@id"]]
                        relationship = lookup[datum]
                        relations.append(create_relation(node_id,relation_id,relationship))
                        count+=1
                # If it has type and value, it's a property
                if "@value" in result[datum][0].keys():
                    property_name = lookup[datum]
                    property_value = result[datum][0]["@value"]
                    properties.append((property_name,property_value))
            # Now create the node!
            new_node = create_node(node_id,label,result_id,name,properties)
            neo4j.append(new_node.encode("utf-8"))

# Now print to file!
filey = open("%s/graph.gist" %(outfolder),'w')
filey.writelines("= %s\n:neo4j-version: 2.0.0\n:author: Nidash Working Group\n:twitter: @nidm\n:tags: nidm:nidash:informatics:neuroimaging:data-structure\n'''\nThis is a neo4j graph to show the turtle file %s.\n'''\n[source, cypher]\n----\n" %(ttl_file,ttl_file))
for node in neo4j:
    filey.writelines(node)
for relation in relations:
    filey.writelines(relation)
filey.writelines("----\n//graph\nWe can use cypher to query the graph, here is an example to select the first 25 atLocation relationships:\n[source, cypher]\n----\nMATCH ()-[r:ATLOCATION]->() RETURN r LIMIT 25\n----\n//table\n'''\nHere is an interactive console for you to explore the graph\n\n//console\n'''\n\n== NIDM Working Group\n* link:http://http://nidm.nidash.org/[NIDM Standard]")
filey.close()

# Now write a Readme to link the gist
filey = open("%s/README.md" %(outfolder),'w')
filey.writelines("### %s\n" %(ttl_file))
filey.writelines("[view graph](http://gist.neo4j.org/?github-"+ username + "%2F" + repo_name + "%2F%2F" + outfolder + "%2Fgraph.gist)\n")
filey.close()
