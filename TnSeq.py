import pandas as pd


HIT_FILENAME = "07 - WildType1.wig"
OUTPUT_FILENAME = "feature_hit_table.csv"
FEATURES_FILENAME = "SGD_features.tab"


class Feature:
    def __init__(self, name, chromosome, start, stop):
        self.name = name
        self.chromosome = chromosome
        self.start = start
        self.stop = stop

        
def get_features(feature_db_filename):
    """Returns a list of Feature objects."""
    
    result = []
    
    feature_table = pd.read_csv(FEATURES_FILENAME, sep="\t")
    
    # Necessary column indices inferred from:
    # https://downloads.yeastgenome.org/curation/chromosomal_feature/SGD_features.README
    for _, row in feature_table.iterrows():
        name = row[0]
        chromosome = row[8]
        start = row[9]
        stop = row[10]
        
        if not start or not stop or not chromosome:
            continue
            
        try:
            start = int(start)
            stop = int(stop)
        except:
            continue
        
        result.append(Feature(name, chromosome, start, stop))
    
    return result
        

def find_features(chromosome, hit_position, feature_list):
    """Given a chromosome and the hit position, return a list of hit Features
    (or an empty list, if none were hit)."""

    result = []
    
    for feature in feature_list:
        if feature.chromosome == chromosome and feature.start <= hit_position <= feature.stop:
            result.append(feature)
            
        assert feature.start < feature.stop
    
    return result

def get_hits(hit_wig_filename):
    """Return a list of (chromosome, hit position) tuples."""

    result = []
    
    chromosome = None
    with open(hit_wig_filename, "r") as wig_file:
        wig_file.readline() # Skip the first header line
        for line in wig_file:
            if line.startswith("variableStep"):
                chromosome = line.split()[1].split('=')[-1].strip()
                continue
                
            result.append((chromosome, int(line.split()[0])))
    
    return result

def main():
    feature_list = get_features(FEATURES_FILENAME)
    hits = get_hits(HIT_FILENAME)
    
    hits_table = pd.DataFrame(
        columns=["Feature", "Hits"],
        data=[(feature.name, 0) for feature in feature_list]
    )
    hits_table.set_index("Feature", inplace=True)
    
    for chromosome, hit_position in hits:
        features = find_features(chromosome, hit_position, feature_list)
        for feature in features:
            hits_table.loc[feature.name]["Hits"] += 1
    
    hits_table.to_csv(OUTPUT_FILENAME)

if __name__ == "__main__":
    main()