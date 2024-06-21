
DROP TABLE IF EXISTS Publicaciones;
CREATE TABLE Publicaciones (
    id INT NOT NULL PRIMARY KEY,
    contenido VARCHAR(1000),
    fecha_publicacion TIMESTAMP,
    tipo VARCHAR(20),
    likes INT
);

INSERT INTO Publicaciones (id,contenido,fecha_publicacion,tipo,likes)
VALUES (1,"hola mundo",17/06/2024,"Imagen",200);
