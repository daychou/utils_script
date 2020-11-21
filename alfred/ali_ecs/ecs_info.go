package main

import (
	"github.com/levigross/grequests"
	"github.com/pkg/errors"
)

const (
	token = "xxx"
	url   = "https://aa.com/cmdb/v2/api/assets/cloud_host/"
)

type HostInfo struct {
	Results []struct {
		Name string `json:"name"`
		IP   string `json:"ip"`
	} `json:"results"`
}

func GetCloudHost() (*HostInfo, error) {
	var hostInfo *HostInfo

	ro := &grequests.RequestOptions{
		Params: map[string]string{
			"simple":    "1",
			"page_size": "9999",
			"type":      "9",
		},
		Headers:   map[string]string{"Authorization": "Token " + token},
		UserAgent: "Alfred of daychou",
	}
	resp, err := grequests.Get(url, ro)
	if err != nil {
		return hostInfo, errors.Wrap(err, "request get error: ")
	}

	if err := resp.JSON(&hostInfo); err != nil {
		return hostInfo, errors.Wrap(err, "json Unmarshal error: ")
	}

	return hostInfo, nil
}
