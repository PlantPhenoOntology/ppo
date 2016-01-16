curl http://data.biscicol.org/ds/data?graph=urn:uuid:dbac5796-900d-4e39-93af-931803f0409a  > single.n3
rapper single.n3 -i turtle -o dot > single.dot
dot2vue single.dot > single.vue
