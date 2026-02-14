import ast
from flask import Flask, render_template, request
import google.generativeai as genai
from flask import send_file
import io
from datetime import datetime



app = Flask(__name__)


genai.configure(api_key="APIKEY")
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
@app.route("/download")
def download():
    content = request.args.get("content", "")
    file_stream = io.BytesIO()
    file_stream.write(content.encode("utf-8"))
    file_stream.seek(0)
    return send_file(file_stream, as_attachment=True, download_name="docstrings.txt", mimetype="text/plain")
def generate_project_doc(output, style):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"Docstring Generator Output\nStyle: {style}\nGenerated on: {timestamp}\n\n"
    return header + output

if __name__ == "__main__":
    app.run(debug=True)
