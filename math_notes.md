# Math Notes - TreeShell Address Space

## User's Verbatim Explanation

"yeah nav determines whcih are accessible from nav... and numeric coordinates are what nav is a tree of. think of it like this, there is a tree called 0 which is what the families represent, and the families are themselves a forest called Family, where all nodes have semantic labels. Family is then restricted by a filter called nav config which is a list, and the output of that restriction is a conversion to a single tree called nav, and the conversion process is the called building numeric coordinates. This tree nav is just the semantic tree 0 represented as a numerical tree. Now the system resolves 2 address types. Then, we have zones, which is a digraph that can arbitrarily group any IDs from nav or 0, and takes meaning based declared semantic names. These can be arbitrary, but the objective is to group them by meaning; the system resolves 3 address types. Then we have combo nodes, which are the combinations of semantic and numerical; these are separate from zone and zone do not combine into the others because a zone already contains any of the others. Ok? So the end product is a graph equipped with 3 dimensions: tree 0, tree nav, and digraph zone config (we probably want to rename this to realm or something made of zones)."

## Key Mathematical Concepts

- **Tree 0**: The families (semantic forest)
- **Nav**: Filtered + converted numerical tree from Tree 0  
- **Zone config/Realm**: Digraph grouping nodes by meaning
- **3 address types**: Semantic, numerical, realm-based
- **Combo nodes**: Semantic + numerical combinations (separate from zones)
- **Zone containment**: Zones already contain other address types, no further combination needed