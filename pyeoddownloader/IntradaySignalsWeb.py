from flask import *
import pandas as pd
app = Flask(__name__)

@app.route("/tables")
def show_tables():
    data = pd.read_excel('merged.xlsx')
    data.set_index(['SYMBOL'], inplace=True)
    data.index.name=None
    
    
    return render_template('view.html',tables=[data.to_html()],
    titles = ['na', 'Female surfers', 'Male surfers'])

if __name__ == "__main__":
    app.run(debug=True)