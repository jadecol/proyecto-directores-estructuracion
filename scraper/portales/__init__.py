"""
scraper/portales/ — adaptadores de cada portal de empleo
Cada módulo expone una función buscar_<portal>(busqueda, ciudad, playwright_context)
que retorna lista de dicts crudos con estructura homogénea.
"""
from .computrabajo import buscar_computrabajo
from .magneto import buscar_magneto
from .linkedin import buscar_linkedin
from .elempleo import buscar_elempleo
