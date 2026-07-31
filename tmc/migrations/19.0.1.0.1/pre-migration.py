def migrate(cr, version):
    # name dropped translate=True. If an earlier 19.0 state left it as a
    # translated JSONB column, convert it to plain varchar under a controlled
    # window; the code is identical across languages, so it is lossless.
    cr.execute(
        "SELECT data_type FROM information_schema.columns "
        "WHERE table_name = 'tmc_document' AND column_name = 'name'"
    )
    row = cr.fetchone()
    if row and row[0] == "jsonb":
        cr.execute(
            "ALTER TABLE tmc_document ALTER COLUMN name TYPE varchar "
            "USING COALESCE(name->>'en_US', name->>'es_AR')"
        )
