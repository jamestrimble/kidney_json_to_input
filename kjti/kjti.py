import argparse
import json

class KidneyConversionError(Exception):
    pass

class Patient(object):
    def __init__(self, id, paired_donors):
        self.id = id
        self.paired_donors = paired_donors

def convert(instance):
    paired_donors = []
    ndds = []
    for id in instance:
        if "altruistic" in instance[id] and instance[id]["altruistic"]:
            ndds.append(instance[id])
            ndds[-1]["id"] = int(id)
        else:
            donor = instance[id]
            paired_donors.append(donor)
            donor["id"] = int(id)
            if len(donor["sources"]) > 1:
                raise KidneyConversionError(
                        "Donor {} has more than one source.".format(id))

    patient_ids_set = set()
    for donor in paired_donors:
        patient_ids_set.update(donor["sources"])
    patient_ids = sorted(patient_ids_set)

    patients = []
    for id in patient_ids:
        patient = Patient(id, [])
        patients.append(patient)
        for donor in paired_donors:
            if donor["sources"][0] == id:
               patient.paired_donors.append(donor)

    pair_pair_edges = set() 
    for i, patient in enumerate(patients):
        for donor in patient.paired_donors:
            if "matches" in donor:
                for match in donor["matches"]:
                    target = patient_ids.index(match["recipient"])
                    if i == target:
                        raise KidneyConversionError(
                                "Self-loop found: patient {}.".format(i))
                    pair_pair_edges.add((i, target, 1))

    ndd_pair_edges = []
    for i, ndd in enumerate(ndds):
        if "matches" in ndd:
            for match in ndd["matches"]:
                try:
                    target = patient_ids.index(match["recipient"])
                    ndd_pair_edges.append((i, target, 1))
                except ValueError:
                    # If target patient doesn't exist, just keep going
                    pass

    write_edges(len(patients), sorted(pair_pair_edges))
    write_edges(len(ndds), ndd_pair_edges)
    

def write_edges(n, edges):
    """Writes an instance in .input or .ndds format

    Args:
        n: Number of donor-patient pairs (for .input) or NDDs (for .ndds)
        edges: The edges in (src_as_int, tgt_as_int, weight_as_float) format
    """

    print "{}\t{}".format(n, len(edges))
    for edge in edges:
        print "{}\t{}\t{}".format(edge[0], edge[1], edge[2])

    print "-1\t-1\t-1"

if __name__=="__main__":
    parser = argparse.ArgumentParser(
            "Convert a kidney-exchange instance from JSON format to combined"
            ".input and .ndds format. Each donor must have at most one paired"
            "patient. Donor-patient pairs with the same patient are combined.")
    parser.add_argument("filename",
            help="the name of the input .json file")
            
    args = parser.parse_args()

    with open(args.filename) as f:
        data = json.load(f)

    convert(data["data"])
