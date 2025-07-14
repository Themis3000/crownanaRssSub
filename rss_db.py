import psycopg2

conn = psycopg2.connect(database="postgres",
                        host="localhost",
                        user="postgres",
                        password="postgres",
                        port=5432)

cursor = conn.cursor()
cursor.execute("""
SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='feeds');
""")
if not cursor.fetchone()[0]:
    print("no tables found.")
    cursor.execute("""
    create table feeds
    (
        feed_id        serial                     not null
            constraint feeds_pk
                primary key,
        config_url     varchar(2000)              not null
            constraint config_url_key
                unique,
        addition_date  timestamp(0) default NOW() not null,
        interval       integer      default 43200 not null,
        last_completed integer      default 0     not null,
    
        next_run integer generated always as ( last_completed + interval ) stored
    );
    
    create index next_run_index
        on feeds (next_run);
    
    create index config_url_index
        on feeds (config_url);
    """)
    cursor.close()
    conn.commit()
else:
    print("table already exists")
