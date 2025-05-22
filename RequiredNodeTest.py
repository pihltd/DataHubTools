import bento_mdf

modelfiles = [r"C:\Users\pihltd\Documents\modeltest\CDS700Req\cds-model.yml", r"C:\Users\pihltd\Documents\modeltest\CDS700Req\cds-model-props.yml"]

testmdf = bento_mdf.mdf.MDF(*modelfiles)
nodes = testmdf.model.nodes

reqnodes = []
optnodes = []

for node in nodes:
    tags = nodes[node].tags
    if 'nodeReq' in tags:
        if (tags['nodeReq'].get_attr_dict())['value'] == 'Yes':
            reqnodes.append(node)
        else:
            optnodes.append(node)
    else:
        optnodes.append(node)

print(f"Required Nodes: {reqnodes}\nOptional Nodes: {optnodes}")
    