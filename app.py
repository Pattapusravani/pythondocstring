import ast
from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)


genai.configure(api_key="AIzaSyCznuVDu_5y8g6KuX9450vTVhBRe28yDC4")
model = genai.GenerativeModel("gemini-2.5-flash")

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    history = []

    if request.method == "POST":
        file = request.files["file"]
        style = request.form["style"]
        code = file.read().decode("utf-8")

        tree = ast.parse(code)
        results = []

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                existing_doc = ast.get_docstring(node)

                if existing_doc:
                    results.append(
                        f"Function: {func_name}\nExisting Docstring:\n{existing_doc}\n"
                    )
                else:
                    # Generate docstring using Gemini
                    prompt = f"Generate a {style} style docstring for:\n{ast.unparse(node)}"
                    response = model.generate_content(prompt)
                    results.append(
                        f"Function: {func_name}\nGenerated Docstring:\n{response.text}\n"
                    )

        output = "\n".join(results)
        history.append({"style": style, "result": output})

    return render_template("index.html", output=output, history=history)

if __name__ == "__main__":
    app.run(debug=True)