package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"os/exec"
	"time"

	aw "github.com/deanishe/awgo"
	"go.deanishe.net/fuzzy"
)

var (
	cacheName   = "ecs.json"        // Filename of cached repo list
	maxResults  = 10                // Number of results sent to Alfred
	maxCacheAge = 180 * time.Minute // How long to cache repo list for

	// Command-line flags
	doDownload bool
	query      string

	// Workflow
	sopts []fuzzy.Option
	wf    *aw.Workflow
)

func init() {
	flag.BoolVar(&doDownload, "download", false, "Read host information from cmdb")

	// Set some custom fuzzy search options
	sopts = []fuzzy.Option{
		fuzzy.AdjacencyBonus(10.0),
		fuzzy.LeadingLetterPenalty(-0.1),
		fuzzy.MaxLeadingLetterPenalty(-3.0),
		fuzzy.UnmatchedLetterPenalty(-0.5),
	}
	wf = aw.New(aw.HelpURL("https://github.com/daychou/utils_script"),
		aw.MaxResults(maxResults),
		aw.SortOptions(sopts...))
}

func run() {
	wf.Args() // call to handle any magic actions
	flag.Parse()

	if args := flag.Args(); len(args) > 0 {
		query = args[0]
	}

	if doDownload {
		wf.Configure(aw.TextErrors(true))
		log.Printf("[main] downloading ecs list...")
		hostInfos, err := GetCloudHost()
		if err != nil {
			wf.FatalError(err)
		}
		if err := wf.Cache.StoreJSON(cacheName, hostInfos); err != nil {
			wf.FatalError(err)
		}
		log.Printf("[main] downloaded ecs list")
		return
	}

	log.Printf("[main] query=%s", query)

	// Try to load repos
	var ecsList []*hostInfo
	if wf.Cache.Exists(cacheName) {
		if err := wf.Cache.LoadJSON(cacheName, &ecsList); err != nil {
			wf.FatalError(err)
		}
	}

	// If the cache has expired, set Rerun (which tells Alfred to re-run the
	// workflow), and start the background update process if it isn't already
	// running.
	if wf.Cache.Expired(cacheName, maxCacheAge) {
		wf.Rerun(0.3)
		if !wf.IsRunning("download") {
			cmd := exec.Command(os.Args[0], "-download")
			if err := wf.RunInBackground("download", cmd); err != nil {
				wf.FatalError(err)
			}
		} else {
			log.Printf("download job already running.")
		}
		// Cache is also "expired" if it doesn't exist. So if there are no
		// cached data, show a corresponding message and exit.
		if len(ecsList) == 0 {
			wf.NewItem("Downloading ecs info…").
				Icon(aw.IconInfo)
			wf.SendFeedback()
			return
		}
	}

	// Add results for cached ecs
	for _, r := range ecsList {
		sub := fmt.Sprintf("★ %s(%s)", r.IP, r.Status)
		wf.NewItem(r.Name).
			Match(r.Name+r.IP).
			Subtitle(sub).
			Arg(r.IP).
			UID(r.IP).
			Valid(true).
			Var("hostname", r.Name)
	}

	// Filter results against query if user entered one
	if query != "" {
		res := wf.Filter(query)
		log.Printf("[main] %d/%d ecs match %q", len(res), len(ecsList), query)
	}

	// Convenience method that shows a warning if there are no results to show.
	// Alfred's default behaviour if no results are returned is to show its
	// fallback searches, which is also what it does if a workflow errors out.
	//
	// As such, it's a good idea to display a message in this situation,
	// otherwise the user can't tell if the workflow failed or simply found
	// no matching results.
	wf.WarnEmpty("No ecs found", "Try a different query?")

	// Send results/warning message to Alfred
	wf.SendFeedback()
}

func main() {
	wf.Run(run)
}
