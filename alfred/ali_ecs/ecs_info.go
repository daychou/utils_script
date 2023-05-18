package main

type hostInfo struct {
	Name   string `json:"name"`
	IP     string `json:"ip"`
	Status string `json:"status"`
}

func GetCloudHost() ([]*hostInfo, error) {
	var hostInfos []*hostInfo

	instances, err := getAliyunECS()
	if err != nil {
		return hostInfos, err
	}

	for i := range instances {
		var ip string
		if *instances[i].InstanceNetworkType == "classic" {
			ip = *instances[i].InnerIpAddress.IpAddress[0]
		} else {
			ip = *instances[i].VpcAttributes.PrivateIpAddress.IpAddress[0]
		}
		hostInfos = append(hostInfos, &hostInfo{
			Name:   *instances[i].InstanceName,
			IP:     ip,
			Status: *instances[i].Status,
		})
	}
	return hostInfos, nil
}
