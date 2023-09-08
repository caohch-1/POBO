local function recommend()
  wrk.headers["Connection"] = "Keep-Alive"
  local coin = math.random()
  local req_param = ""
  if coin < 0.33 then
    req_param = "dis"
  elseif coin < 0.66 then
    req_param = "rate"
  else
    req_param = "price"
  end

  local lat = 38.0235 + (math.random(0, 481) - 240.5)/1000.0
  local lon = -122.095 + (math.random(0, 325) - 157.0)/1000.0

  local path = "/recommendations?require=" .. req_param .. 
    "&lat=" .. tostring(lat) .. "&lon=" .. tostring(lon)
  local headers = {}
  -- headers["Content-Type"] = "application/x-www-form-urlencoded"
  return wrk.format("GET", path)
end

request = function()
  return recommend()
end