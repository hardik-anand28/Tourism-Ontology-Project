from rdflib import Graph, URIRef, Literal, Namespace
import pandas as pd
import sys
import os

def csv_to_ttl(csv_path, output_ttl_path, base_namespace="http://mynewtourismontology.org#"):
    g = Graph()
    MY = Namespace(base_namespace)

    try:
        print(f"Loading CSV from {csv_path}...")
        # Load CSV with string dtype and handle missing values as empty strings
        df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
        df = df.fillna("")  # Replace any NaN with empty string

        # Check required columns
        required_columns = ['subject', 'predicate', 'object']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"CSV must contain columns: {required_columns}")

        # Process each row
        for index, row in df.iterrows():
            subject_str = str(row['subject']).strip()
            predicate_str = str(row['predicate']).strip()
            obj_str = str(row['object']).strip()

            # Convert to RDF terms
            subject = URIRef(subject_str) if subject_str else None
            predicate = URIRef(predicate_str) if predicate_str else None
            if not subject or not predicate:
                print(f"Skipping invalid triple at row {index}: {row}")
                continue

            # Handle object as URI or Literal
            if obj_str.startswith('http://') or obj_str.startswith('https://'):
                obj = URIRef(obj_str)
            else:
                datatype = row.get('datatype', None)
                language = row.get('language', None)
                if datatype:
                    obj = Literal(obj_str, datatype=URIRef(datatype))
                elif language:
                    obj = Literal(obj_str, lang=language)
                else:
                    # Check for numeric literals
                    if obj_str.replace('.', '').replace('-', '').replace('E', '').isdigit():
                        obj = Literal(float(obj_str), datatype=URIRef("http://www.w3.org/2001/XMLSchema#double"))
                    else:
                        obj = Literal(obj_str)

            g.add((subject, predicate, obj))
            if index % 10000 == 0:
                print(f"Processed {index} triples...")

        # Check if output directory is writable
        output_dir = os.path.dirname(output_ttl_path) or '.'
        if not os.access(output_dir, os.W_OK):
            raise PermissionError(f"No write permission in {output_dir}")

        print(f"Saving to {output_ttl_path}...")
        g.serialize(destination=output_ttl_path, format='turtle')
        print(f"Successfully converted {len(g)} triples to {output_ttl_path}")

    except Exception as e:
        print(f"Error: {type(e).__name__} - {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <csv_file_path> <output_ttl_path>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    output_ttl_path = sys.argv[2]
    csv_to_ttl(csv_path, output_ttl_path)