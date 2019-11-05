package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
)

// ClusterSpec represents the parameters for eksctl,
// as cluster metadata including owner and how long the cluster
// still has to live.
type ClusterSpec struct {
	// ID is a unique identifier for the cluster
	ID string `json:"id"`
	// Name specifies the cluster name
	Name string `json:"name"`
	// S3Bucket specifies the bucket to store config
	S3Bucket string `json:"s3bucket"`
	// Iamrole specifies the Iam role to specify in the kubeconfig
	Iamrole string `json:"iamrole"`
	// NumWorkers specifies the number of worker nodes, defaults to 1
	Autoscaling map[string]int `json:"autoscaling"`
	// NumWorkers specifies the number of worker nodes, defaults to 1
	NumWorkers int `json:"numworkers"`
	// KubeVersion  specifies the Kubernetes version to use, defaults to `1.12`
	KubeVersion string `json:"kubeversion"`
	// Command used to build your kubeconfig locally
	CliCommand string `json:"clicommand"`
	// Addons from selection screen
	Addons map[string]bool `json:"addons"`
}

var ekspcp string
var cscache map[string]ClusterSpec

func main() {
	cscache = make(map[string]ClusterSpec)
	pinfo(fmt.Sprintf("Result proloning the cluster lifetime: %v", cscache))
	http.Handle("/", http.FileServer(http.Dir("./frontend")))
	http.HandleFunc("/status", StatusCluster)
	http.HandleFunc("/list", ListCluster)
	http.HandleFunc("/create", CreateCluster)
	http.HandleFunc("/delete", DeleteCluster)
	http.HandleFunc("/configof", GetClusterConfig)
	log.Println("EKSphemeral UI up and running on http://localhost:8080/")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		panic(err)
	}
}

// pinfo writes msg in light blue to stderr
// see also https://misc.flogisoft.com/bash/tip_colors_and_formatting
func pinfo(msg string) {
	_, _ = fmt.Fprintf(os.Stdout, "\x1b[94m%v\x1b[0m\n", msg)
}

// perr writes message (and optionally error) in light red to stderr
// see also https://misc.flogisoft.com/bash/tip_colors_and_formatting
func perr(msg string, err error) {
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "%v: \x1b[91m%v\x1b[0m\n", msg, err)
		return
	}
	_, _ = fmt.Fprintf(os.Stderr, "\x1b[91m%v\x1b[0m\n", msg)
}
