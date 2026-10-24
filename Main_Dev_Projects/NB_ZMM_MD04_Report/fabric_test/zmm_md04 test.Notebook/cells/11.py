
v = spark.table("sap_zmm_md04_vigente")
print(f"{v.count()} filas · {len(v.columns)} columnas")
print(sorted(v.columns))

# Lo que el matching necesita
for c in ["Pedido", "Posición", "Referencia", "Tipo_Confirmacion", "Cantidad",
          "Precio_Neto", "monto_linea", "Family", "Proveedor",
          "Nombre_del_Proveedor", "Centro", "Material"]:
    print(f"  {c:<22}{'SI' if c in v.columns else 'NO'}")

# Y los tipos, que importan para las llaves
v.select("Pedido", "Posición", "Referencia", "Cantidad", "Precio_Neto").printSchema()
v.select("Pedido", "Posición", "Referencia").show(5, False)

