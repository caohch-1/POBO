-- require "socket"
-- math.randomseed(socket.gettime()*1000)
-- math.random(); math.random(); math.random()

local function get_user()
  local id = math.random(0, 500)
  local user_name = "Cornell_" .. tostring(id)
  local pass_word = ""
  for i = 0, 9, 1 do 
    pass_word = pass_word .. tostring(id)
  end
  return user_name, pass_word
end

local function search_hotel()
  wrk.headers["Connection"] = "Keep-Alive" 
  local in_date = math.random(9, 23)
  local out_date = math.random(in_date + 1, 24)

  local in_date_str = tostring(in_date)
  if in_date <= 9 then
    in_date_str = "2015-04-0" .. in_date_str 
  else
    in_date_str = "2015-04-" .. in_date_str
  end

  local out_date_str = tostring(out_date)
  if out_date <= 9 then
    out_date_str = "2015-04-0" .. out_date_str 
  else
    out_date_str = "2015-04-" .. out_date_str
  end

  local lat = 38.0235 + (math.random(0, 481) - 240.5)/1000.0
  local lon = -122.095 + (math.random(0, 325) - 157.0)/1000.0

  local method = "GET"
  local path = "/hotels?inDate=" .. in_date_str .. 
    "&outDate=" .. out_date_str .. "&lat=" .. tostring(lat) .. "&lon=" .. tostring(lon)

  return wrk.format("GET", path)
end

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
  return wrk.format("GET", path)
end

local function reserve()
  local in_date = math.random(9, 23)
  local out_date = in_date + math.random(1, 5)

  local in_date_str = tostring(in_date)
  if in_date <= 9 then
    in_date_str = "2015-04-0" .. in_date_str 
  else
    in_date_str = "2015-04-" .. in_date_str
  end

  local out_date_str = tostring(out_date)
  if out_date <= 9 then
    out_date_str = "2015-04-0" .. out_date_str 
  else
    out_date_str = "2015-04-" .. out_date_str
  end

  local hotel_id = tostring(math.random(1, 80))
  local user_id, password = get_user()
  local cust_name = user_id

  local num_room = "1"

  local method = "POST"
  local path = "http://localhost:35587/reservation?inDate=" .. in_date_str .. 
    "&outDate=" .. out_date_str .. "&lat=" .. tostring(lat) .. "&lon=" .. tostring(lon) ..
    "&hotelId=" .. hotel_id .. "&customerName=" .. cust_name .. "&username=" .. user_id ..
    "&password=" .. password .. "&number=" .. num_room
  local headers = {}
  -- headers["Content-Type"] = "application/x-www-form-urlencoded"
  return wrk.format(method, path, headers, nil)
end

local function user_login()
  wrk.headers["Connection"] = "Keep-Alive"
  local user_name, password = get_user()
  local path = "/user?username=" .. user_name .. "&password=" .. password
  return wrk.format("GET", path)
end

request = function()
  local search_ratio      = 0.33
  local recommend_ratio   = 0.33
  local user_ratio        = 0.34
  local reserve_ratio     = 0

  local coin = math.random()
  if coin < search_ratio then
    return search_hotel()
  elseif coin < search_ratio + recommend_ratio then
    return recommend()
  elseif coin < search_ratio + recommend_ratio + user_ratio then
    return user_login()
  else 
    return reserve()
  end
end