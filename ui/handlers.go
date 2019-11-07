package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"time"
)

// ListCluster invokes the /list endpoint listing all cluster specs in bucket
func ListCluster(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		w.Write([]byte(`Allow: ` + "POST"))
		return
	}
	s3bucket := getBucket()
	cs := ClusterSpec{}
	cs.S3Bucket = s3bucket
	c := &http.Client{
		Timeout: time.Second * 3,
	}
	ekspcp := getEndpoint()
	req, err := json.Marshal(cs)
	pres, err := c.Post(ekspcp+"/list/", "application/json", bytes.NewBuffer(req))
	pinfo(fmt.Sprintf("Posting to %v/list/ with status clusterspec %v", ekspcp, cs))
	if err != nil {
		perr("Can't POST to control plane for list all", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		jsonResponse(w, http.StatusInternalServerError, "Can't POST to control plane for cluster list")
		return
	}
	defer pres.Body.Close()
	body, err := ioutil.ReadAll(pres.Body)
	if err != nil {
		perr("Can't read control plane response for cluster list", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		jsonResponse(w, http.StatusInternalServerError, "Can't read control plane response for cluster list")
		return
	}
	pinfo(fmt.Sprintf("Result listing the clusters %v", string(body)))
	defer pres.Body.Close()
	jsonResponse(w, http.StatusOK, string(body))
}

// StatusCluster invokes the /status endpoint in the EKSBoot returning EKS details derived from boto3
func StatusCluster(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		w.WriteHeader(http.StatusMethodNotAllowed)
		w.Write([]byte(`Allow: ` + "GET"))
		return
	}
	fmt.Fprintf(os.Stdout, "\x1b[94m Recieved this get URL:%v\x1b[0m\n", r.URL)
	fmt.Fprintf(os.Stdout, "\x1b[94m Recieved this get body:%v\x1b[0m\n", r.Body)
	q := r.URL.Query()
	targetcluster := q.Get("cluster")
	pinfo(fmt.Sprintf("Received status lookup request for %v cluster", targetcluster))
	// cs, err := lookup(targetcluster) // try local cache
	// if err == nil {
	// 	csjson, err := json.Marshal(cs)
	// 	if err != nil {
	// 		perr("Can't marshal cluster spec data", err)
	// 		http.Error(w, err.Error(), http.StatusInternalServerError)
	// 		jsonResponse(w, http.StatusInternalServerError, "Can't marshal cluster spec data")
	// 		return
	// 	}
	// 	pinfo("Serving from cache")
	// 	jsonResponse(w, http.StatusOK, string(csjson))
	// 	return
	// }
	ekspcp := getEndpoint()
	pinfo(fmt.Sprintf("Using %v as the control plane endpoint", ekspcp))
	c := &http.Client{
		Timeout: time.Second * 30,
	}
	pres, err := c.Get(ekspcp + "/status/" + targetcluster)
	if err != nil {
		perr("Can't GET control plane for cluster status", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		jsonResponse(w, http.StatusInternalServerError, "Can't GET control plane for cluster status")
		return
	}
	defer pres.Body.Close()
	body, err := ioutil.ReadAll(pres.Body)
	if err != nil {
		perr("Can't read control plane response for cluster status", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		jsonResponse(w, http.StatusInternalServerError, "Can't read control plane response for cluster status")
		return
	}
	pinfo(fmt.Sprintf("Status for cluster: %v", string(body)))
	jsonResponse(w, http.StatusOK, string(body))
}

// CreateCluster sanitizes user input, provisions the EKS cluster using the /create endpoint
// This kicks off the CDK temlpate and pipeline to provision the EKS cluster
func CreateCluster(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		w.Write([]byte(`Allow: ` + "POST"))
		return
	}
	fmt.Fprintf(os.Stdout, "\x1b[94m Recieved this post URL:%v\x1b[0m\n", r.URL)
	decoder := json.NewDecoder(r.Body)
	cs := ClusterSpec{}
	err := decoder.Decode(&cs)
	s3bucket := getBucket()
	cs.S3Bucket = s3bucket
	if err != nil {
		perr("Can't parse cluster spec from UI", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		jsonResponse(w, http.StatusInternalServerError, "Can't parse cluster spec from UI")
		return
	}
	fmt.Fprintf(os.Stdout, "\x1b[94m From the web UI I got the following values for cluster create: %+v\x1b[0m\n", cs)
	c := &http.Client{
		Timeout: time.Second * 300,
	}
	req, err := json.Marshal(cs)
	if err != nil {
		perr("Can't marshal cluster spec data", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		jsonResponse(w, http.StatusInternalServerError, "Can't marshal cluster spec data")
		return
	}
	ekspcp := getEndpoint()
	pinfo(fmt.Sprintf("Posting to %v/create/ with status clusterspec %v", ekspcp, cs))
	pres, err := c.Post(ekspcp+"/create/", "application/json", bytes.NewBuffer(req))
	if err != nil {
		perr("Can't POST to control plane for cluster create", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		jsonResponse(w, http.StatusInternalServerError, "Can't POST to control plane for cluster create")
		return
	}
	defer pres.Body.Close()
	body, err := ioutil.ReadAll(pres.Body)
	if err != nil {
		perr("Can't read control plane response for cluster create", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		jsonResponse(w, http.StatusInternalServerError, "Can't read control plane response for cluster create")
		return
	}
	defer pres.Body.Close()
	jsonResponse(w, http.StatusOK, string(body))
}

// GetClusterConfig returns the cluster config for based off most recent clusterspec in the bucket
func GetClusterConfig(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		w.Write([]byte(`Allow: ` + "POST"))
		return
	}
	q := r.URL.Query()
	targetcluster := q.Get("cluster")
	s3bucket := getBucket()
	cs := ClusterSpec{}
	cs.S3Bucket = s3bucket
	req, err := json.Marshal(cs)
	ekspcp := getEndpoint()
	c := &http.Client{
		Timeout: time.Second * 10,
	}
	fmt.Fprintf(os.Stdout, "\x1b[94m Recieved this post URL:%v\x1b[0m\n", r.URL)
	pinfo(fmt.Sprintf("Posting to %v/configof/%v with status clusterspec %v", ekspcp, targetcluster, cs))
	pres, err := c.Post(ekspcp+"/configof/"+targetcluster, "application/json", bytes.NewBuffer(req))
	if err != nil {
		perr("Can't POST configof for cluster", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		jsonResponse(w, http.StatusInternalServerError, "Can't POST configof for cluster")
		return
	}
	defer pres.Body.Close()
	body, err := ioutil.ReadAll(pres.Body)
	if err != nil {
		perr("Can't read configof api for response", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		jsonResponse(w, http.StatusInternalServerError, "Can't read configof api for response")
		return
	}
	jsonResponse(w, http.StatusOK, string(body))
}

// DeleteCluster evokes the delete API endpoint deleting the Cluster
func DeleteCluster(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		w.Write([]byte(`Allow: ` + "POST"))
		return
	}
	fmt.Fprintf(os.Stdout, "\x1b[94m Recieved this post URL:%v\x1b[0m\n", r.URL)
	q := r.URL.Query()
	targetcluster := q.Get("cluster")
	s3bucket := getBucket()
	cs := ClusterSpec{}
	cs.S3Bucket = s3bucket
	cs.Name = targetcluster
	req, err := json.Marshal(cs)
	ekspcp := getEndpoint()
	c := &http.Client{
		Timeout: time.Second * 900,
	}
	pres, err := c.Post(ekspcp+"/delete/"+targetcluster, "application/json", bytes.NewBuffer(req))
	if err != nil {
		perr("Can't GET delete for cluster", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		jsonResponse(w, http.StatusInternalServerError, "Can't GET delete for cluster")
		return
	}
	defer pres.Body.Close()
	body, err := ioutil.ReadAll(pres.Body)
	if err != nil {
		perr("Can't read delete api for response", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		jsonResponse(w, http.StatusInternalServerError, "Can't read delete api for response")
		return
	}
	jsonResponse(w, http.StatusOK, string(body))
}
