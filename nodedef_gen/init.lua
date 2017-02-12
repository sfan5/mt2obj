local function nd_get_tiles(nd)
	local tiles = nd.tiles or nd.tile_images or {}
	for k,v in ipairs(tiles) do
		if type(v) == 'table' then
			tiles[k] = v.name
		end
	end
	return tiles
end

local function nd_get_drawtype(nd)
	return nd.drawtype or "normal"
end

local drawtype_map = {
	["normal"] = "cube",
	["plantlike"] = "plant",
	-- do these actually work?
	["glasslike"] = "cube",
	["allfaces"] = "cube",
	["allfaces_optional"] = "cube",
}

minetest.register_chatcommand("dump", {
	params = "",
	description = "",
	func = function(plname, param)
		local n = 0
		minetest.mkdir("out")
		local out, err = io.open('out/nodes.pre.txt', 'wb')
		if not out then
			return minetest.chat_send_player(plname, 'io.open: ' .. err)
		end

		for nn, nd in pairs(minetest.registered_nodes) do
			local tiles = nd_get_tiles(nd)
			local mapped = drawtype_map[nd_get_drawtype(nd)]
			if mapped ~= nil and #tiles > 0 then
				local texfilename = nn:gsub(":", "__") .. ".png"
				local usable_tex
				if #tiles == 1 then -- TODO multiple tiles
					usable_tex = texfilename
				end
				minetest.generateAndSaveTexture(tiles[1], "out/" .. texfilename)

				usable_tex = usable_tex and ("texture=" .. usable_tex) or ":"
				out:write(string.format("%s %s - - - %s %s\n", nn, mapped, usable_tex, texfilename))
				n = n + 1
			end
		end

		out:close()
		minetest.chat_send_player(plname, n .. " nodes dumped.")
	end,
})
