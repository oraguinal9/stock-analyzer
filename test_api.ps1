$body = @{query="比亚迪 002594"; select_type="A 股"} | ConvertTo-Json
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/stock/query" -Method POST -Body $body -ContentType "application/json"
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
