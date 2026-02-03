
import argparse
import pandas as pd
import json
import os

def main():

    # Causal pathways dictionary
	causal_pathways = {
        "Social better": {
            "@id": "https://repo.metadatacenter.org/template-instances/8302e75d-ab21-4613-b94a-89c0eaf54c39",
            "schema:name": "Social Better"
        },
         "Social gain": {
            "@id": "https://repo.metadatacenter.org/template-instances/46d968d8-762f-4870-bb05-3321a9b69f14",
            "schema:name": "Social Gain"
        },
        "Social worse": {
            "@id": "https://repo.metadatacenter.org/template-instances/f4006042-5750-4f6c-a039-fe0a88466464",
            "schema:name": "Social Worse"
        },
        "Social loss": 
        {
            "@id": "https://repo.metadatacenter.org/template-instances/88f49c3d-9f82-4134-9237-ac6eb0dec69f",
            "schema:name": "Social Loss"
        },
        "Social approach": 
        {
            "@id": "https://repo.metadatacenter.org/template-instances/0884af75-ed8c-4b61-aa15-67b41b93d834",
            "schema:name": "Social Approach"
        },
        "Goal better": 
        {
            "@id": "https://repo.metadatacenter.org/template-instances/deb62b84-bd40-4729-84ca-bf099cc2c07x4k",
            "schema:name": "Goal Better"
        },
        "Goal gain": 
        {
            "@id": "https://repo.metadatacenter.org/template-instances/deb62b84-bd40-4729-84ca-bf099cc2c07e",
            "schema:name": "Goal Gain"
        },
        "Goal worse": 
        {
            "@id": "http://example.com/goal_worse_temporary",
            "schema:name": "Goal Worse"
        },
        "Goal loss": 
        {
            "@id": "https://repo.metadatacenter.org/template-instances/d3159028-f58f-4bc2-bc44-8279263db82b",
            "schema:name": "Goal Loss"
        },
        "Goal approach": 
        {
            "@id": "https://repo.metadatacenter.org/template-instances/66c607b6-800b-4071-8a0a-627110f698e2",
            "schema:name": "Goal Approach"
        },
        "Improving": {
            "@id": "https://repo.metadatacenter.org/template-instances/0b160448-c376-476d-b4a9-5e8a5496eaf0",
            "schema:name": "Improving"
        },
        "Worsening": 
        {
            "@id": "https://repo.metadatacenter.org/template-instances/f20f522c-3c0d-4eea-b459-95b8404051d5",
            "schema:name": "Worsening"
        }
        
	}
	parser = argparse.ArgumentParser(description="Knowledge Base Generator")
	parser.add_argument('--knowledge_base_path', default="/home/faridsei/dev/test/Yidan/kb/kb.xlsx", type=str, help='Path to the knowledge base Excel file')
	args = parser.parse_args()

	# Read the Excel file
	xlsx_path = args.knowledge_base_path
	try:
		xls = pd.ExcelFile(xlsx_path)
	except Exception as e:
		print(f"Error reading Excel file: {e}")
		return

	# Extract the required sheets
	try:
		performance_measures_df = pd.read_excel(xls, sheet_name="Performance Measures")
	except Exception as e:
		print(f"Error reading 'Performance Measures' sheet: {e}")
		performance_measures_df = None

	try:
		message_templates_df = pd.read_excel(xls, sheet_name="Message Templates")
	except Exception as e:
		print(f"Error reading 'Message Templates' sheet: {e}")
		message_templates_df = None



	# Generate measures.json from template and performance_measures_df
	if performance_measures_df is not None:
		template_path = os.path.join(os.path.dirname(__file__), 'templates/measures.json')
		with open(template_path, 'r') as f:
			measures_template = json.load(f)

		measures = []
		for _, row in performance_measures_df.iterrows():
			measure_id = str(row.get('Measure ID', '')).strip()
			measure_name = str(row.get('Measure Name', '')).strip()
			desired_direction = str(row.get('Desired Direction', '')).strip().lower()
			if not measure_id or not measure_name or not desired_direction:
				continue
			if desired_direction.startswith('increas'):
				direction_uri = "http://purl.obolibrary.org/obo/PSDO_desired_increasing_measure"
			elif desired_direction.startswith('decreas'):
				direction_uri = "http://purl.obolibrary.org/obo/PSDO_desired_decreasing_measure"
			else:
				direction_uri = ""
			measure_obj = {
				"@id": f"_:{measure_id}",
				"@type": "http://purl.obolibrary.org/obo/PSDO_0000102",
				"dc:title": measure_name,
				"identifier": measure_id,
				"has_desired_direction": direction_uri
			}
			measures.append(measure_obj)

		measures_template["slowmo:IsAboutMeasure"] = measures

		kb_dir = os.path.dirname(os.path.abspath(xlsx_path))
		output_path = os.path.join(kb_dir, "measures.json")
		with open(output_path, 'w') as f:
			json.dump(measures_template, f, indent=2)
		print(f"Generated measures.json with {len(measures)} measures at {output_path}")

	# Generate message.json files from Message Templates tab
	if message_templates_df is not None:
		import uuid
		from datetime import datetime
		msg_template_path = os.path.join(os.path.dirname(__file__), 'templates/message.json')
		with open(msg_template_path, 'r') as f:
			message_template = json.load(f)

		now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S-08:00")
		kb_dir = os.path.dirname(os.path.abspath(xlsx_path))

		for idx, row in message_templates_df.iterrows():
			# Only process rows with is_about containing at least one object

			is_about_col = str(row.get('is_about', '')).strip()
			# Try to parse as a list of JSON objects, even if all in one string
			is_about_objs = []
			if is_about_col:
				# Try to wrap in [] and parse as JSON array
				try:
					# Replace single quotes with double quotes for valid JSON
					is_about_json = '[' + is_about_col + ']'
					is_about_objs = json.loads(is_about_json.replace("'", '"'))
				except Exception:
					# Fallback: try to split by '},' and parse each object
					parts = is_about_col.split('},')
					for i, part in enumerate(parts):
						part = part.strip()
						if not part.endswith('}'): part += '}'
						try:
							is_about_objs.append(json.loads(part.replace("'", '"')))
						except Exception:
							continue
			if not is_about_objs:
				continue

			direction = str(row.get('Desired Direction', '')).strip()
			if direction == "Increasing":
				is_about_objs.append({
					"@id": "http://purl.obolibrary.org/obo/PSDO_desired_increasing_measure",
					"rdfs:label": "desired increase measure"
				})
			elif direction == "Decreasing":
				is_about_objs.append({
					"@id": "http://purl.obolibrary.org/obo/PSDO_desired_decreasing_measure",
					"rdfs:label": "desired decrease measure"
				})
			msg_obj = json.loads(json.dumps(message_template))  # deep copy
			msg_obj['is_about'] = is_about_objs

			# has_causal_pathway from Compatible Causal Pathway column using dictionary
			compatible_causal_pathway = str(row.get('Compatible Causal Pathway', '')).strip()
			if compatible_causal_pathway in causal_pathways:
				msg_obj['has_causal_pathway'] = causal_pathways[compatible_causal_pathway]
			else:
				msg_obj['has_causal_pathway'] = {"@id": "", "schema:name": compatible_causal_pathway}

			# Name and schema:name
			msg_name = str(row.get('Message Template', '')).strip()
			msg_obj['Name'] = {"@value": msg_name}
			msg_obj['schema:name'] = msg_name

			# Message text
			msg_text = str(row.get('Message Text', '')).strip()
			msg_obj['Message text'] = [{"@value": msg_text}]

			# Default display
			default_display = str(row.get('Compatible Visualizations', '')).strip()
			msg_obj['Default display'] = {"@value": default_display}

			# pav:createdOn and pav:lastUpdatedOn
			msg_obj['pav:createdOn'] = now_str
			msg_obj['pav:lastUpdatedOn'] = now_str

			# pav:createdBy, oslc:modifiedBy left blank

			# @id: random UUID
			msg_obj['@id'] = f"https://repo.metadatacenter.org/template-instances/{uuid.uuid4()}"

			# Short message ID: use index or leave as in template
			# Additional message text: leave as in template

			# Write to file
			out_filename = f"{msg_name}.json"
			out_path = os.path.join(kb_dir, out_filename)
			with open(out_path, 'w') as f:
				json.dump(msg_obj, f, indent=2)
			print(f"Generated {out_filename} at {out_path}")

if __name__ == "__main__":
	main()
