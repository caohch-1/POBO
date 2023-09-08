local function get_user()
  local id = math.random(0, 500)
  local user_name = "Cornell_" .. tostring(id)
  local pass_word = ""
  for i = 0, 9, 1 do 
    pass_word = pass_word .. tostring(id)
  end
  return user_name, pass_word
end

local function user_login()
  local user_name, password = get_user()
  wrk.headers["Connection"] = "Keep-Alive"
  local path = "/user?username=" .. user_name .. "&password=" .. password
  local headers = {}
  -- wrk.headers["Content-Type"] = "application/x-www-form-urlencoded"
  local tmp = wrk.format("GET", path)

  return tmp
end

request = function()
  return user_login()
end