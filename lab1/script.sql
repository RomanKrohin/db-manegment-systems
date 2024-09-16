DO $$
DECLARE
    current_user TEXT;
    target_user TEXT;
    table_name TEXT;
    row_number INTEGER := 1;
    has_tables BOOLEAN := FALSE;
    target_user_exists BOOLEAN;
BEGIN
    SELECT current_user INTO current_user;

    target_user := <target_user>;

    SELECT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = target_user
    ) INTO target_user_exists;

    IF NOT target_user_exists THEN
        RAISE NOTICE 'Target user does not exist.';
        RETURN;
    END IF;


    RAISE NOTICE 'Current user: %', current_user;
    RAISE NOTICE 'User to grant access rights: %', target_user;
    RAISE NOTICE 'No. Table name';
    RAISE NOTICE '--- -------------------------';

    FOR table_name IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = current_user
          AND EXISTS (
              SELECT 1
              FROM pg_class c
              JOIN pg_roles r ON c.relowner = r.oid
              WHERE c.relname = pg_tables.tablename
                AND r.rolname = current_user
          )
    LOOP
        RAISE NOTICE '% %', row_number, table_name;
        row_number := row_number + 1;
        has_tables := TRUE;
    END LOOP;

    IF NOT has_tables THEN
        RAISE NOTICE 'No tables on which the current user can grant access rights.';
    END IF;
END $$;
