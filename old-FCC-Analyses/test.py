import ROOT
from argparse import ArgumentParser


parser = ArgumentParser()

parser.add_argument(
    "--input-file",
    required=True,
    help="Input EDM4hep ROOT file.",
)

parser.add_argument(
    "--output-file",
    required=True,
    help="Output reduced ROOT file.",
)

parser.add_argument(
    "--max-events",
    type=int,
    default=100,
    help="Maximum number of events to process.",
)

args = parser.parse_args()

input_list = [args.input_file]


# Load FCCAnalyses
ROOT.gSystem.Load("libFCCAnalyses")

if ROOT.dummyLoader:
    print("----> DEBUG: Found FCCAnalyses library.")

    ROOT.gInterpreter.Declare(
        "using namespace FCCAnalyses::PodioSource;"
    )

print("----> INFO: Loading analyzers from libFCCAnalyses...")


# Load podio DataSource
if ROOT.podio.DataSource:
    print("----> DEBUG: Found Podio ROOT DataSource.")

print("----> INFO: Loading events through podio::DataSource...")


# Create dataframe
dframe = ROOT.podio.CreateDataFrame(input_list)

# Limit events while debugging
if args.max_events is not None:
    dframe = dframe.Range(args.max_events)


# Example PodioSource analysis
dframe = dframe.Define(
    "electron_truth",
    "ReconstructedParticle::selPDG(11)(RecoMCLink)",
)

dframe = dframe.Define(
    "electron_truth_pt",
    "ReconstructedParticle::getPt(electron_truth)",
)


# Columns to save
branches = [
    "electron_truth_pt",
]


# Configure Snapshot to write an RNTuple
snapshot_options = ROOT.RDF.RSnapshotOptions()

snapshot_options.fOutputFormat = (
    ROOT.RDF.ESnapshotOutputFormat.kRNTuple
)


# Write reduced RNTuple
dframe.Snapshot(
    "events",
    args.output_file,
    branches,
    snapshot_options,
)


print(
    f"Saved reduced RNTuple to {args.output_file}"
)
