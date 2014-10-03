local function nd_get_tiles(nd)
	local tiles
	if nd.tiles then
		tiles = nd.tiles
	elseif nd.tile_images then
		tiles = nd.tile_images
	end
	--if type(tiles) == 'table' then
	--	tiles = tiles.name
	--end
	if tiles == nil then
		tiles = {}
	end
	return tiles
end

minetest.register_chatcommand("dump", {
	params = "",
	description = "",
	func = function(plname, param)
		local n = 0
		local out, err = io.open('nodes.pre.txt', 'wb')
		if not out then
			return minetest.chat_send_player(plname, 'io.open: ' .. err)
		end
		for nn, nd in pairs(minetest.registered_nodes) do
			if nd.drawtype == nil or nd.drawtype == "normal" then
				local tiles = nd_get_tiles(nd)
				local texprefix = nn:gsub(":", "__")
				--[[
				for i, t in ipairs(tiles) do
					minetest.generateAndSaveTexture(t, texprefix .. i .. ".png")
				end
				--]]
				if #tiles == 1 then
					out:write(nn .. " cube - - - texture=" .. texprefix .. ".png " .. texprefix .. ".png\n")
					minetest.generateAndSaveTexture(tiles[1], texprefix .. ".png")
					n = n + 1
				else
					-- TODO
				end
			end
		end
		out:close()
		minetest.chat_send_player(plname, n .. " nodes dumped.")
	end,
})
