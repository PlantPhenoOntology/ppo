curl http://data.biscicol.org/ds/data?graph=urn:uuid:dbac5796-900d-4e39-93af-931803f0409a  > NEON_observation.n3
rapper NEON_observation.n3 -i turtle -o dot > NEON_observation.dot
dot2vue NEON_observation.dot > NEON_observation.vue
