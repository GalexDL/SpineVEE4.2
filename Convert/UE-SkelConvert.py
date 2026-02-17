import json
import sys
from pathlib import Path

# Usage: py UE-SkelConvert.py <input.json> [models.json]

def extract_spine_unreal(json_path, models_json_path=None):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    atlas = next((item for item in data if item.get('Type') == 'SpineAtlasAsset'), None)
    skel = next((item for item in data if item.get('Type') == 'SpineSkeletonDataAsset'), None)

    if not atlas or not skel:
        print('Could not find both atlas and skeleton data in the file.')
        return

    # Extract atlas
    atlas_raw = atlas['Properties']['rawData']
    atlas_filename = Path(json_path).with_suffix('.atlas')
    with open(atlas_filename, 'w', encoding='utf-8') as f:
        f.write(atlas_raw)
    print(f'Atlas data written to {atlas_filename}')

    # Extract skeleton (skel) as binary
    skel_raw = skel['Properties']['rawData']
    skel_filename = Path(json_path).with_suffix('.skel')
    with open(skel_filename, 'wb') as f:
        f.write(bytes(skel_raw))
    print(f'Skeleton data written to {skel_filename}')

    # Also write skeleton data as JSON for inspection
    skel_json_filename = Path(json_path).with_suffix('.skel.json')
    with open(skel_json_filename, 'w', encoding='utf-8') as f:
        json.dump(skel_raw, f, ensure_ascii=False, indent=2)
    print(f'Skeleton data (JSON array) written to {skel_json_filename}')

    # Optionally update models.json
    if models_json_path:
        model_entry = {
            "name": Path(json_path).stem,
            "data": str(skel_filename.relative_to(Path(models_json_path).parent)),
            "atlas": str(atlas_filename.relative_to(Path(models_json_path).parent))
        }
        with open(models_json_path, 'r', encoding='utf-8') as f:
            models = json.load(f)
        models.append(model_entry)
        with open(models_json_path, 'w', encoding='utf-8') as f:
            json.dump(models, f, ensure_ascii=False, indent=4)
        print(f'Models.json updated with new entry: {model_entry}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python extract_spine_unreal.py <input.json> [models.json]')
    else:
        extract_spine_unreal(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)