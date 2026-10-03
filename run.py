from college_ai import discover_colleges
from flask import jsonify, request
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
@app.route('/colleges', methods=['GET'])
def get_colleges():
    query = request.args.get('q', '').strip()
    state = request.args.get('state', '').strip()

    # 1. First, search your existing database (if you have one)
    # results = search_in_your_database(query)
    results = []

    # 2. If college not found in database, automatically discover and return with AI!
    auto_saved_count = 0
    if not results and query:
        ai_colleges = discover_colleges(query, state)
        if ai_colleges:
            results = ai_colleges
            auto_saved_count = len(ai_colleges)
            # (Optional: insert results into your database here)

    return jsonify({
        "success": True,
        "total": len(results),
        "autoUpdatedToDb": auto_saved_count,
        "results": results
    })
