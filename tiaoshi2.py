import re,json
a = {"outerId": "5f17ff473c97c299dcfab2e5", "inlineIds": '', "autoAudit": 'true'}
b = re.findall('(?<="outerId": ").*?(?=")', json.dumps(a))
print(b)
