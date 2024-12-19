// This file is auto-generated, don't edit it. Thanks.
package main

import (
	openapi "github.com/alibabacloud-go/darabonba-openapi/v2/client"
	ecs20140526 "github.com/alibabacloud-go/ecs-20140526/v3/client"
	util "github.com/alibabacloud-go/tea-utils/v2/service"
	"github.com/alibabacloud-go/tea/tea"
)

/**
 * 使用AK&SK初始化账号Client
 * @param accessKeyId
 * @param accessKeySecret
 * @return Client
 * @throws Exception
 */
func CreateClient(accessKeyId *string, accessKeySecret *string) (_result *ecs20140526.Client, _err error) {
	config := &openapi.Config{
		// 必填，您的 AccessKey ID
		AccessKeyId: accessKeyId,
		// 必填，您的 AccessKey Secret
		AccessKeySecret: accessKeySecret,
	}
	// 访问的域名
	config.Endpoint = tea.String("ecs-cn-hangzhou.aliyuncs.com")
	_result = &ecs20140526.Client{}
	_result, _err = ecs20140526.NewClient(config)
	return _result, _err
}

func getAliyunECS() (instances []*ecs20140526.DescribeInstancesResponseBodyInstancesInstance, _err error) {
	// 工程代码泄露可能会导致AccessKey泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议使用更安全的 STS 方式，更多鉴权访问方式请参见：https://help.aliyun.com/document_detail/378661.html
	client, _err := CreateClient(tea.String("xxx"), tea.String("xxx"))
	if _err != nil {
		return instances, _err
	}

	describeInstancesRequest := &ecs20140526.DescribeInstancesRequest{
		RegionId:   tea.String("cn-hangzhou"),
		MaxResults: tea.Int32(100),
	}

	//var data = make([]*ecs20140526.DescribeInstancesResponseBodyInstancesInstance, 0)
	for hasNextpage, marker := true, ""; hasNextpage != false; {
		describeInstancesRequest.NextToken = tea.String(marker)
		runtime := &util.RuntimeOptions{}
		tryErr := func() (_e error) {
			defer func() {
				if r := tea.Recover(recover()); r != nil {
					_e = r
				}
			}()
			// 复制代码运行请自行打印 API 的返回值
			resp, _err := client.DescribeInstancesWithOptions(describeInstancesRequest, runtime)
			if _err != nil {
				return _err
			}

			if *resp.Body.NextToken == "" {
				hasNextpage = false
			} else {
				marker = *resp.Body.NextToken
			}

			instances = append(instances, resp.Body.Instances.Instance...)

			return nil
		}()

		if tryErr != nil {
			var err = &tea.SDKError{}
			if _t, ok := tryErr.(*tea.SDKError); ok {
				err = _t
			} else {
				err.Message = tea.String(tryErr.Error())
			}
			return instances, err
		}
	}

	return instances, _err
}
