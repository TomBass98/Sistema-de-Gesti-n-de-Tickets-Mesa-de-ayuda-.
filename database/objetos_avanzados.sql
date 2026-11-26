    USE mesa_ayuda;

    -- 1. TRIGGER: Si el estado cambia a 'Cerrado', pone la fecha y hora exacta automáticamente

    DELIMITER //
    CREATE TRIGGER trg_fecha_cierre_ticket
    BEFORE UPDATE ON tbl_tickets_servicio
    FOR EACH ROW
    BEGIN
        IF NEW.estado = 'Cerrado' AND OLD.estado <> 'Cerrado' THEN
            SET NEW.fecha_cierre = NOW();
        END IF;
    END //
    DELIMITER ;

    -- 2. evita costos negativos

    DELIMITER //
    CREATE TRIGGER trg_validar_costo_ticket
    BEFORE INSERT ON tbl_tickets_servicio
    FOR EACH ROW
    BEGIN
        IF NEW.costo_total < 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: El costo total del ticket no puede ser negativo.';
        END IF;
    END //
    DELIMITER ;


    -- 3. Procedimiento que nos crea un ticket y devuelve su id
    DELIMITER //
    CREATE PROCEDURE sp_crear_ticket(
        IN p_falla VARCHAR(255),
        IN p_costo DECIMAL(10,2),
        IN p_id_equipo INT,
        IN p_id_tecnico INT,
        OUT p_nuevo_id INT
    )
    BEGIN
        INSERT INTO tbl_tickets_servicio (falla_reportada, costo_total, id_equipo, id_tecnico)
        VALUES (p_falla, p_costo, p_id_equipo, p_id_tecnico);
        
        SET p_nuevo_id = LAST_INSERT_ID();
    END //
    DELIMITER ;

    -- 5. Vista que nos trae el resumen de los tickets

    CREATE OR REPLACE VIEW vw_reporte_tickets AS
    SELECT 
        t.id_ticket,
        t.fecha_ingreso,
        t.fecha_cierre,
        t.estado,
        t.falla_reportada,
        t.costo_total,
        c.nombre_cli AS cliente,
        c.documento_cli,
        e.tipo_equipo,
        e.marca,
        e.modelo,
        e.serial_number,
        tec.nombre_tec AS tecnico_asignado,
        tec.especialidad
    FROM tbl_tickets_servicio t
    INNER JOIN tbl_equipos e ON t.id_equipo = e.id_equipo
    INNER JOIN tbl_clientes c ON e.id_cliente = c.id_cliente
    INNER JOIN tbl_tecnicos tec ON t.id_tecnico = tec.id_tecnico;

