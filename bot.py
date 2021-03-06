import discord
import pafy
from discord.ext import commands
import asyncio
import youtube_dl
import socket

class Player(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.song_que = {}

		self.setup()

	def setup(self):
		for guild in self.bot.guilds:
			self.song_que[guild.id] = []

	async def play_song(self, ctx, song):
		'''url = pafy.new(song).getbestaudio().url
		newurl = url.split('/')
		socketed = socket.gethostbyname(url[2])
		print(socketed+"/"+newurl[3])
		''''''counter = 0
		for x in newurl:
			print(counter)
			print(x)
			counter +=1'''
		#FFMpeg_options = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options":"-vn"}
		#source = await discord.FFmpegOpusAudio.from_probe(url, **FFMpeg_options)
		#ctx.voice_client.play(source, after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
		#print(url)
		#ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url)), after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
		#ctx.voice_client.source.volume = 0.5
		ydl_options = {"format":"bestaudio/best"}

		with youtube_dl.YoutubeDL(ydl_options) as ydl:
			info = ydl.extract_info(song, download = False)
			url2 = info['formats'][0]['url']
			ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url2, options="-framerate 60 -probesize 72M")), after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
			if len(self.song_que[ctx.guild.id]) > 0:
			  await ctx.send(f"Now playing: {song}")
			#source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMpeg_options)
			#ctx.voice_client.play(source, after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))

		#ctx.voice_client.source.volume = 0.5

	async def check_queue(self, ctx):
		#await ctx.send("a song has passed")
		if len(self.song_que[ctx.guild.id]) > 0:
		  await self.play_song(ctx, self.song_que[ctx.guild.id][0])
		  self.song_que[ctx.guild.id].pop(0)
		else:
		  #await ctx.send("deleted that fucker")
		  ctx.voice_client.stop()

	async def search_song(self, amount, song, get_url=False):
		info = await self.bot.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL({"format" : "bestaudio", "quiet" : True}).extract_info(f"ytsearch{amount}:{song}", download=False, ie_key="YoutubeSearch"))
		if len(info["entries"]) == 0: return None

		return [entry["webpage_url"] for entry in info["entries"]] if get_url else info

	@commands.command()
	async def join(self, ctx):
		if ctx.author.voice is None:
			return await ctx.send("You gotta be in a damn vc stupid")

		if ctx.voice_client is not None:
			await ctx.voice_client.disconnect()

		await ctx.author.voice.channel.connect()

	@commands.command()
	async def disconnect(self, ctx):
		if ctx.voice_client is not None:
			return await ctx.voice_client.disconnect()
		await ctx.send("Luna is not connected to a channel")

	@commands.command()
	async def tester(self, ctx, *, song=None):
		result = await self.search_song(1, song, get_url=True)

		await ctx.send(result)

	@commands.command()
	async def play(self, ctx, *, song=None):
		if song is None:
			return await ctx.send("You must include a song to play.")

		if ctx.author.voice is None:
			return await ctx.send("You gotta be in a damn vc stupid")

		if ctx.voice_client is None:
			await ctx.author.voice.channel.connect()

		# handle song where song isn't url
		if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
			await ctx.send("Luna is searching for the song")

			result = await self.search_song(1, song, get_url=True)

			if result is None:
				return await ctx.send("Sorry, Luna tried her best shit not working")

			song = result[0]

		if ctx.voice_client.source is not None:
			queue_len = len(self.song_que[ctx.guild.id])

			if queue_len < 10:
				self.song_que[ctx.guild.id].append(song)
				return await ctx.send(f"this song has been added to the queue at position: {queue_len+1}.")

			else:
				return await ctx.send("Sorry, I can only queue up to 10 songs, please wait for the current song to finish.")

		#await ctx.send(song)
		await self.play_song(ctx, song)
		await ctx.send(f"Now playing: {song}")

	@commands.command()
	async def skip(self, ctx):
		if ctx.voice_client is None:
			return await ctx.send("Luna is not playing anything rn")

		if ctx.author.voice is None:
			return await ctx.send("You gotta be in a damn vc stupid")

		if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
			return await ctx.send("Luna is not playing anything for you atm")

		ctx.voice_client.stop()

	@commands.command()
	async def stop(self, ctx):
	  self.song_que[ctx.guild.id].clear()
	  ctx.voice_client.stop()
  
	@commands.command()
	async def test(self, ctx):
	  return await ctx.send(ctx.voice_client.source)
	  print(self.song_que[ctx.guild.id])
  