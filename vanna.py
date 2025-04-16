# %%
from vanna.ollama import Ollama
from vanna.qdrant import Qdrant_VectorStore
from qdrant_client import QdrantClient

class MyVanna(Qdrant_VectorStore, Ollama):
    def __init__(self, config=None):
        Qdrant_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

vn = MyVanna(config={'client': QdrantClient(url='sensor',api_key='sensor'), 'model': 'llama3:8b'})

# %%
vn.connect_to_mysql(host='localhost', dbname='test', user='root',password='',port=3306)

# %%
# df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")

# %%
# plan = vn.get_training_plan_generic(df_information_schema)
# vn.train(plan=plan)

# %%
# vn.train(ddl="""
#     
# """)

# vn.ask(question='column term ada berapa ditable buybackworld')
from vanna.flask import VannaFlaskApp
app = VannaFlaskApp(vn)
app.run()

# %%
# The following are methods for adding training data. Make sure you modify the examples to match your database.

# DDL statements are powerful because they specify table names, colume names, types, and potentially relationships
# vn.train(ddl="""
#     CREATE TABLE IF NOT EXISTS my-table (
#         id INT PRIMARY KEY,
#         name VARCHAR(100),
#         age INT
#     )
# """)

# Sometimes you may want to add documentation about your business terminology or definitions.
# vn.train(documentation="Our business defines OTIF score as the percentage of orders that are delivered on time and in full")

# You can also add SQL queries to your training data. This is useful if you have some queries already laying around. You can just copy and paste those from your editor to begin generating new SQL.
# vn.train(sql="SELECT * FROM my-table WHERE name = 'John Doe'")

# %%
# At any time you can inspect what training data the package is able to reference
# training_data = vn.get_training_data()
# training_data


