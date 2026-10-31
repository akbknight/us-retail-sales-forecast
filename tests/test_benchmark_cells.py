import json
import re
import os
import sys

def test_retail_benchmark_consistency():
    repo_dir = r"C:\Users\Akshay Kumar\Downloads\Akshay\Projects and Code\us-retail-sales-forecast"
    json_path = os.path.join(repo_dir, "reports", "forecast_benchmark_results.json")
    html_path = os.path.join(repo_dir, "index.html")

    assert os.path.exists(json_path), f"JSON file missing: {json_path}"
    assert os.path.exists(html_path), f"HTML file missing: {html_path}"

    with open(json_path, "r", encoding="utf-8") as f:
        bench_data = json.load(f)

    with open(html_path, "r", encoding="utf-8") as f:
        html_text = f.read()

    val_by_model = {item["model"]: item for item in bench_data["validation_benchmark"]}
    test_by_model = {item["model"]: item for item in bench_data["holdout_test_benchmark"]}
    stored = bench_data["stored_recomputed"]

    # 1. Assert all 8 models exist in JSON
    expected_models = [
        "Holt nonseasonal",
        "Drift",
        "Damped Holt nonseasonal",
        "ETS additive seasonal",
        "ETS damped seasonal",
        "Last value",
        "Seasonal naive",
        "Linear trend"
    ]
    assert len(val_by_model) == 8, f"Expected 8 models in validation, found {len(val_by_model)}"
    assert len(test_by_model) == 8, f"Expected 8 models in test, found {len(test_by_model)}"
    for em in expected_models:
        assert em in val_by_model, f"Missing model in validation: {em}"
        assert em in test_by_model, f"Missing model in test: {em}"

    # 2. Extract benchmark tables from HTML
    tables = re.findall(r'<table class="benchmark-table">(.*?)</table>', html_text, re.DOTALL)
    assert len(tables) >= 2, f"Expected at least 2 benchmark tables (primary + production), found {len(tables)}"

    primary_table_html = tables[0]
    production_table_html = tables[1]

    # Parse primary table rows
    rows = re.findall(r'<tr(?: class="selected-model-row")?>(.*?)</tr>', primary_table_html, re.DOTALL)
    # The first row in <thead> is headers; <tbody> rows have <td>
    body_rows = [r for r in rows if '<td' in r]
    assert len(body_rows) == 8, f"Expected exactly 8 rows in primary benchmark table, found {len(body_rows)}"

    print(f"Verified primary benchmark table has exactly {len(body_rows)} rows.")

    # Check each model row
    model_mapping = {
        "Damped Nonseasonal Holt": "Damped Holt nonseasonal",
        "Nonseasonal Holt": "Holt nonseasonal",
        "Simple Drift": "Drift",
        "Additive Seasonal ETS": "ETS additive seasonal",
        "Damped Seasonal ETS": "ETS damped seasonal",
        "Last Value (Random Walk)": "Last value",
        "Seasonal Naïve": "Seasonal naive",
        "Seasonal Na&iuml;ve": "Seasonal naive",
        "Linear Trend (Full History)": "Linear trend"
    }

    verified_count = 0
    for r in body_rows:
        cells = [re.sub(r'<.*?>', '', c).strip() for c in re.findall(r'<td.*?>(.*?)</td>', r, re.DOTALL)]
        assert len(cells) == 8, f"Expected 8 columns per row, got {len(cells)}: {cells}"
        
        display_name = cells[0]
        category = cells[1]
        val_mae_str = cells[2]
        val_mape_str = cells[3]
        test_mae_str = cells[4]
        test_mape_str = cells[5]
        test_rmse_str = cells[6]
        status_note = cells[7]

        # Find corresponding model key by exact display name
        matched_key = model_mapping.get(display_name)
        if not matched_key:
            for k, v in model_mapping.items():
                if k == display_name:
                    matched_key = v
                    break
        assert matched_key is not None, f"Unknown model name in table: {display_name}"

        expected_val = val_by_model[matched_key]
        expected_test = test_by_model[matched_key]

        # Validate numbers
        parsed_val_mae = float(re.search(r'\$([0-9.]+)B', val_mae_str).group(1))
        parsed_val_mape = float(re.search(r'([0-9.]+)%', val_mape_str).group(1))
        parsed_test_mae = float(re.search(r'\$([0-9.]+)B', test_mae_str).group(1))
        parsed_test_mape = float(re.search(r'([0-9.]+)%', test_mape_str).group(1))
        parsed_test_rmse = float(re.search(r'\$([0-9.]+)B', test_rmse_str).group(1))

        assert abs(parsed_val_mae - expected_val['MAE_billions']) < 0.005, f"{matched_key} val MAE mismatch: {parsed_val_mae} vs {expected_val['MAE_billions']}"
        assert abs(parsed_val_mape - expected_val['MAPE_pct']) < 0.05, f"{matched_key} val MAPE mismatch: {parsed_val_mape} vs {expected_val['MAPE_pct']}"
        assert abs(parsed_test_mae - expected_test['MAE_billions']) < 0.005, f"{matched_key} test MAE mismatch: {parsed_test_mae} vs {expected_test['MAE_billions']}"
        assert abs(parsed_test_mape - expected_test['MAPE_pct']) < 0.005, f"{matched_key} test MAPE mismatch: {parsed_test_mape} vs {expected_test['MAPE_pct']}"
        assert abs(parsed_test_rmse - expected_test['RMSE_billions']) < 0.005, f"{matched_key} test RMSE mismatch: {parsed_test_rmse} vs {expected_test['RMSE_billions']}"

        print(f"  [PASS] {matched_key:25}: Val ${parsed_val_mae:.3f}B ({parsed_val_mape:.2f}%) | Test ${parsed_test_mae:.3f}B ({parsed_test_mape:.3f}%) | RMSE ${parsed_test_rmse:.3f}B")
        verified_count += 1

    assert verified_count == 8, f"Expected 8 verified models, got {verified_count}"

    # 3. Check Production table
    prod_rows = re.findall(r'<tr(?: class=".*?")?>(.*?)</tr>', production_table_html, re.DOTALL)
    prod_body_rows = [r for r in prod_rows if '<td' in r]
    assert len(prod_body_rows) == 1, f"Expected 1 row in production table, got {len(prod_body_rows)}"

    prod_cells = [re.sub(r'<.*?>', '', c).strip() for c in re.findall(r'<td.*?>(.*?)</td>', prod_body_rows[0], re.DOTALL)]
    assert len(prod_cells) == 8, f"Expected 8 cells in production row, got {len(prod_cells)}"

    assert "Not evaluated" in prod_cells[2], f"Expected 'Not evaluated' in val MAE, got {prod_cells[2]}"
    assert "Not evaluated" in prod_cells[3], f"Expected 'Not evaluated' in val MAPE, got {prod_cells[3]}"

    prod_test_mae = float(re.search(r'\$([0-9.]+)B', prod_cells[4]).group(1))
    prod_test_mape = float(re.search(r'([0-9.]+)%', prod_cells[5]).group(1))
    prod_test_rmse = float(re.search(r'\$([0-9.]+)B', prod_cells[6]).group(1))

    assert abs(prod_test_mae - stored["MAE_billions"]) < 0.005, f"Prod MAE mismatch: {prod_test_mae} vs {stored['MAE_billions']}"
    assert abs(prod_test_mape - stored["MAPE_pct"]) < 0.005, f"Prod MAPE mismatch: {prod_test_mape} vs {stored['MAPE_pct']}"
    assert abs(prod_test_rmse - stored["RMSE_billions"]) < 0.005, f"Prod RMSE mismatch: {prod_test_rmse} vs {stored['RMSE_billions']} (must be $9.928B)"
    assert prod_cells[6] == "$9.928B", f"Exact string must be $9.928B, got {prod_cells[6]}"

    print(f"  [PASS] Production Pipeline: Val [Not evaluated] | Test ${prod_test_mae:.3f}B ({prod_test_mape:.3f}%) | Holdout RMSE {prod_cells[6]}")

    # 4. Check Selection Narrative in HTML
    assert "lowest pre-holdout validation error" in html_text or "lowest validation error" in html_text
    assert "test-set ranking was not the selection procedure" in html_text

    print("\nALL STRICT PER-CELL CONSISTENCY TESTS PASSED 100%!")

if __name__ == "__main__":
    test_retail_benchmark_consistency()
