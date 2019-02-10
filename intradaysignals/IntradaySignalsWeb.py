from flask import *
import pandas as pd


app = Flask(__name__)

@app.route("/tables")
def show_tables():
    data = pd.read_csv('temp.csv')
    data.set_index(['symbol'], inplace=True)
    data.index.name=None
    return render_template('view.html',data=data);

if __name__ == "__main__":
    app.run(host = '0.0.0.0')