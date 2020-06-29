import pdb
import math
import colorama
from termcolor import cprint,colored
from os import system

colorama.init()

globalTime = 0
mainBlockSize = 0

#Function to check if the val is a number of power 2
def is2Power(val):
	tmp = math.log(val,2)
	if(tmp - int(tmp) == 0):
		return True
	return False

#Memory class to create objects of memory instances
class Memory:
	def __init__(self,memoryVal,memoryAddress,memoryTag,dataTag):
		self.memoryVal = memoryVal
		self.memoryAddress = memoryAddress
		self.memoryTag = memoryTag
		self.dataTag = dataTag
		self.timeStamp = globalTime

	def printMemory(self):
		print(str(self.memoryAddress)+" -> "+str(self.memoryVal)+"| ",end=" ")


#Block Class which stores memory in memoryArr
class Block:
	def __init__(self,blockTag):
		global mainBlockSize

		self.blockSize = mainBlockSize
		self.blockTag = blockTag
		self.crntMemoryCount = 0
		self.memoryArr = []

	#Function to insert in list
	def insertInMemoryArray(self,memoryObj):
		self.memoryArr.append(memoryObj)
		self.crntMemoryCount += 1

	#Function to update in list
	def updateInMemoryArray(self,memoryObj):
		for val in self.memoryArr:
			if(val.memoryAddress == memoryObj.memoryAddress):
				self.memoryArr.remove(val)
				self.memoryArr.append(memoryObj)
				break

	#Function to check if a memory obj is in list
	def isInBlock(self,memoryObj):
		if(self.crntMemoryCount == 0):
			return False
		for val in self.memoryArr:
			if(val.memoryAddress == memoryObj.memoryAddress):
				return True
		return False

	#Function that returns memory object 
	def getFromBlock(self,memoryObj):
		for val in self.memoryArr:
			if(val.memoryAddress == memoryObj.memoryAddress):
				return val

	#Function to print block tag and memory array contents
	def printBlock(self):
		# pdb.set_trace()
		cprint("Block number-> "+str(self.blockTag),"yellow")
		for val in self.memoryArr:
			val.printMemory()
		print()


# class implementing fully associative type of mapping
class FullyAssociative:
	def __init__(self,cacheLinesPrimary,cacheLinesSecondary,blockSize):
		self.cacheLinesPrimary = cacheLinesPrimary
		self.cacheLinesSecondary = cacheLinesSecondary
		self.blockSize = blockSize
		self.cachePrimary = {}
		self.cacheSecondary = {}
		self.crntCacheSizePrimary = 0
		self.crntCacheSizeSecondary = 0
		self.localTimeCheckingPrimary = []
		self.localTimeCheckingSecondary = []

	#Function to check if the block is in primary cache
	def isInPrimaryCache(self,blockTag):
		if(self.crntCacheSizePrimary == 0):
			return False

		for val in self.cachePrimary:
			if(val == blockTag):
				return True
		return False

	#Function to check if the block is in secondary cache
	def isInSecondaryCache(self,blockTag):
		if(self.crntCacheSizeSecondary == 0):
			return False

		for val in self.cacheSecondary:
			if(val == blockTag):
				return True
		return False

	#Function to update primary local time checking
	def updateLocalTimeCheckingPrimary(self,blockTag):
		for val in self.localTimeCheckingPrimary:
			if(val == blockTag):
				self.localTimeCheckingPrimary.remove(val)
				break
		self.localTimeCheckingPrimary.append(blockTag)

	#Function to update secondary time checking
	def updateLocalTimeCheckingSecondary(self,blockTag):
		for val in self.localTimeCheckingSecondary:
			if(val == blockTag):
				self.localTimeCheckingSecondary.remove(val)
				break
		self.localTimeCheckingSecondary.append(blockTag)

	#Function to write in cache
	def writeToCache(self,memoryObj,blockTagPrimary,blockTagSecondary):
		if(self.crntCacheSizePrimary == 0):
			cprint("Cache miss in primary cache","yellow")
			cprint("Cache miss in secondary cache","yellow")
			self.crntCacheSizePrimary += 1
			tmpBlock = Block(blockTagPrimary)
			tmpBlock.insertInMemoryArray(memoryObj)
			self.cachePrimary[blockTagPrimary] = tmpBlock
			self.localTimeCheckingPrimary.append(blockTagPrimary)

		elif(self.isInPrimaryCache(blockTagPrimary) == True):
			cprint("Cache hit in primary cache","green")
			cprint("Cache miss in secondary cache","yellow")
			for val in self.cachePrimary:
				if(val == blockTagPrimary):
					if(self.cachePrimary[val].isInBlock(memoryObj) == True):
						self.cachePrimary[val].updateInMemoryArray(memoryObj)
					else:
						self.cachePrimary[val].insertInMemoryArray(memoryObj)
					break
			self.updateLocalTimeCheckingPrimary(blockTagPrimary)

		elif(self.isInPrimaryCache(blockTagPrimary) == False and self.isInSecondaryCache(blockTagSecondary) == False):
			cprint("Cache miss in primary cache","yellow")
			cprint("Cache miss in secondary cache","yellow")

			tmpBlock = Block(blockTagPrimary)
			tmpBlock.insertInMemoryArray(memoryObj)

			if(self.crntCacheSizePrimary < self.cacheLinesPrimary):
				self.cachePrimary[blockTagPrimary] = tmpBlock
				self.localTimeCheckingPrimary.append(blockTagPrimary)
				self.crntCacheSizePrimary += 1

			elif(self.crntCacheSizePrimary >= self.cacheLinesPrimary and self.crntCacheSizeSecondary<self.cacheLinesSecondary):
				blockTagPoppedPrimary = self.localTimeCheckingPrimary.pop(0)
				blockPoppedPrimary = self.cachePrimary[blockTagPoppedPrimary]
				cprint("Currently primary cache is full so using LRU policy to delete the oldest block from cache","yellow")
				cprint("The memory block deleted from the cache is: "+str(blockTagPoppedPrimary),"yellow")
				cprint("contents","yellow")
				blockPoppedPrimary.printBlock()

				for val in self.cachePrimary:
					if(val == blockTagPoppedPrimary):
						tmpDeletedBlock = self.cachePrimary.pop(val)
						break

				cprint("Inserting the block in secondary cache","yellow")
				self.cacheSecondary[blockTagPoppedPrimary] = blockPoppedPrimary
				self.crntCacheSizeSecondary += 1
				self.localTimeCheckingSecondary.append(blockTagPoppedPrimary)

				self.cachePrimary[blockTagPrimary] = tmpBlock
				self.localTimeCheckingPrimary.append(blockTagPrimary)

			elif(self.crntCacheSizePrimary >= self.cacheLinesPrimary and self.crntCacheSizeSecondary >= self.cacheLinesSecondary):
				blockTagPoppedPrimary = self.localTimeCheckingPrimary.pop(0)
				blockPoppedPrimary = self.cachePrimary[blockTagPoppedPrimary]
				cprint("Currently primary cache is full so using LRU policy to delete the oldest block from cache","yellow")
				cprint("The memory block deleted from the cache is: "+str(blockTagPoppedPrimary),"yellow")
				cprint("contents","yellow")
				blockPoppedPrimary.printBlock()

				print()

				blockTagPoppedSecondary = self.localTimeCheckingSecondary.pop(0)
				blockPoppedSecondary = self.cacheSecondary[blockTagPoppedSecondary]

				cprint("Currently secondary cache is full so using LRU policy to delete the oldest block from cache","yellow")
				cprint("The memory block deleted from the cache is: "+str(blockTagPoppedPrimary),"yellow")
				cprint("contents","yellow")
				blockPoppedSecondary.printBlock()

				for val in self.cachePrimary:
					if(val == blockTagPoppedPrimary):
						tmpDeletedBlock1 = self.cachePrimary.pop(val)
						break

				for val in self.cacheSecondary:
					if(val == blockTagPoppedSecondary):
						tmpDeletedBlock2 = self.cacheSecondary.pop(val)
						break

				self.cacheSecondary[blockTagPoppedPrimary] = blockPoppedPrimary
				self.localTimeCheckingSecondary.append(blockTagPoppedPrimary)

				self.cachePrimary[blockTagPrimary] = tmpBlock
				self.localTimeCheckingPrimary.append(blockTagPrimary)


		elif(self.isInPrimaryCache(blockTagPrimary) == False and self.isInSecondaryCache(blockTagSecondary) == True):
			cprint("Cache miss in primary cache","yellow")
			cprint("Cache Hit in secondary cache","green")

			# tmpBlock = Block(blockTagPrimary)
			tmpBlock = self.cacheSecondary.pop(blockTagPrimary)
			tmpBlock.updateInMemoryArray(memoryObj)

			for val in self.localTimeCheckingSecondary:
				if(val == blockTagPrimary):
					self.localTimeCheckingSecondary.remove(val)
					break


			if(self.crntCacheSizePrimary >= self.cacheLinesPrimary and self.crntCacheSizeSecondary<self.cacheLinesSecondary):
				blockTagPoppedPrimary = self.localTimeCheckingPrimary.pop(0)
				self.localTimeCheckingSecondary.append(blockTagPoppedPrimary)
				# print(self.localTimeCheckingPrimary)
				self.localTimeCheckingPrimary.append(blockTagSecondary)
				# print(self.localTimeCheckingSecondary)
				blockPoppedPrimary = self.cachePrimary.pop(blockTagPoppedPrimary)
				cprint("Currently primary cache is full so using LRU policy to delete the oldest block from cache","yellow")
				cprint("The memory block deleted from the cache is: "+str(blockTagPoppedPrimary),"yellow")
				cprint("contents","yellow")
				blockPoppedPrimary.printBlock()
				print()
				print()
				self.cachePrimary[blockTagPrimary] = tmpBlock

				self.cacheSecondary[blockTagPoppedPrimary] = blockPoppedPrimary


			elif(self.crntCacheSizePrimary >= self.cacheLinesPrimary and self.crntCacheSizeSecondary >= self.cacheLinesSecondary):
				blockTagPoppedPrimary = self.localTimeCheckingPrimary.pop(0)
				self.localTimeCheckingSecondary.append(blockTagPoppedPrimary)
				# print(self.localTimeCheckingPrimary)
				self.localTimeCheckingPrimary.append(blockTagSecondary)
				# print(self.localTimeCheckingSecondary)
				blockPoppedPrimary = self.cachePrimary.pop(blockTagPoppedPrimary)
				cprint("Currently primary cache is full so using LRU policy to delete the oldest block from cache","yellow")
				cprint("The memory block deleted from the cache is: "+str(blockTagPoppedPrimary),"yellow")
				cprint("contents","yellow")
				blockPoppedPrimary.printBlock()
				print()
				print()

				self.cachePrimary[blockTagPrimary] = tmpBlock
				self.cacheSecondary[blockTagPoppedPrimary] = blockPoppedPrimary
		
	#Function to read from cache
	def readCache(self,memoryObj,blockTagPrimary,blockTagSecondary):
		if(len(self.cachePrimary) == 0):
			cprint("Primary Cache is empty!!!","yellow")
			return

		if(self.isInPrimaryCache(blockTagPrimary) == True):

			tmpObj = None

			for val in self.cachePrimary:
				if(val == blockTagPrimary):
					found = self.cachePrimary[val].isInBlock(memoryObj)
					if(found == False):
						cprint("The address is not assigned yet","yellow")
						return
					else:
						tmpObj = self.cachePrimary[val]
						break

			for val in tmpObj.memoryArr:
				if(val.memoryAddress == memoryObj.memoryAddress):
					cprint("Cache tag Hit in primary cache","green")
					print("The value at the memory address: "+str(memoryObj.memoryAddress)+" is "+str(val.memoryVal))
					break

			self.updateLocalTimeCheckingPrimary(blockTagPrimary)

		elif(self.isInPrimaryCache(blockTagPrimary) == False and self.isInSecondaryCache(blockTagSecondary) == True):
			cprint("Cache tag miss in primary cache","yellow")
			# cprint("Cache tag Hit in secondary cache","green")
			tmpBlock = self.cacheSecondary.pop(blockTagPrimary)

			for val in self.localTimeCheckingSecondary:
				if(val == blockTagPrimary):
					self.localTimeCheckingSecondary.remove(val)
					break

			tmpFound = False
			for val in tmpBlock.memoryArr:
				if(val.memoryAddress == memoryObj.memoryAddress):
					cprint("Cache tag Hit in primary cache","green")
					print("The value at the memory address: "+str(memoryObj.memoryAddress)+" is "+str(val.memoryVal))
					tmpFound = True
					break

			if(tmpFound == False):
				cprint("The address is not assigned yet","yellow")

			if(self.crntCacheSizePrimary >= self.cacheLinesPrimary and self.crntCacheSizeSecondary<self.cacheLinesSecondary):
				blockTagPoppedPrimary = self.localTimeCheckingPrimary.pop(0)
				self.localTimeCheckingSecondary.append(blockTagPoppedPrimary)
				# print(self.localTimeCheckingPrimary)
				self.localTimeCheckingPrimary.append(blockTagSecondary)
				# print(self.localTimeCheckingSecondary)
				blockPoppedPrimary = self.cachePrimary.pop(blockTagPoppedPrimary)
				cprint("Currently primary cache is full so using LRU policy to delete the oldest block from cache","yellow")
				cprint("The memory block deleted from the cache is: "+str(blockTagPoppedPrimary),"yellow")
				cprint("contents","yellow")
				blockPoppedPrimary.printBlock()
				print()
				print()
				self.cachePrimary[blockTagPrimary] = tmpBlock
				self.cacheSecondary[blockTagPoppedPrimary] = blockPoppedPrimary

			elif(self.crntCacheSizePrimary >= self.cacheLinesPrimary and self.crntCacheSizeSecondary >= self.cacheLinesSecondary):
				blockTagPoppedPrimary = self.localTimeCheckingPrimary.pop(0)
				self.localTimeCheckingSecondary.append(blockTagPoppedPrimary)
				# print(self.localTimeCheckingPrimary)
				self.localTimeCheckingPrimary.append(blockTagSecondary)
				# print(self.localTimeCheckingSecondary)
				blockPoppedPrimary = self.cachePrimary.pop(blockTagPoppedPrimary)
				cprint("Currently primary cache is full so using LRU policy to delete the oldest block from cache","yellow")
				cprint("The memory block deleted from the cache is: "+str(blockTagPoppedPrimary),"yellow")
				cprint("contents","yellow")
				blockPoppedPrimary.printBlock()
				print()
				print()

				self.cachePrimary[blockTagPrimary] = tmpBlock
				self.cacheSecondary[blockTagPoppedPrimary] = blockPoppedPrimary	

		elif(self.isInPrimaryCache(blockTagPrimary) == False and self.isInSecondaryCache(blockTagSecondary) == False):
			cprint("The memory address doesn't exists in either of the caches","yellow")


	#Function to print primary cache
	def printPrimaryCache(self):
		if(len(self.cachePrimary) == 0):
			cprint("Primary Cache is empty!!!","yellow")
			return
		cprint("Primary Cache","cyan")
		count = 1
		for val in self.cachePrimary:
			tmpStr = "Cache Line: "+str(count)
			cprint(tmpStr,"white","on_blue",attrs=["bold"])
			count += 1
			self.cachePrimary[val].printBlock()
		print()

	#Function to print secondary cache
	def printSecondaryCache(self):
		if(len(self.cacheSecondary) == 0):
			cprint("Secondary Cache is empty!!!","yellow")
			return
		cprint("Secondary Cache","cyan")
		count = 1
		for val in self.cacheSecondary:
			tmpStr = "Cache Line: "+str(count)
			cprint(tmpStr,"white","on_blue",attrs=["bold"])
			count += 1
			self.cacheSecondary[val].printBlock()
		print()

	#Function to print both cache
	def printCache(self):
		if(len(self.cachePrimary) == 0):
			cprint("Primary Cache is empty!!!","yellow")
			return
		cprint("Primary cache:","cyan")
		count = 1
		for val in self.cachePrimary:
			tmpStr = "Cache Line: "+str(count)
			cprint(tmpStr,"white","on_blue",attrs=["bold"])
			count += 1
			self.cachePrimary[val].printBlock()
		print()
		print()
		print()
		if(len(self.cacheSecondary) == 0):
			cprint("Secondary Cache is empty!!!","yellow")
			return
		cprint("Secondary cache:","cyan")
		count = 1
		for val in self.cacheSecondary:
			tmpStr = "Cache Line: "+str(count)
			cprint(tmpStr,"white","on_blue",attrs=["bold"])
			count += 1
			self.cacheSecondary[val].printBlock()


#Class to implement Direct Mapping
class DirectMapping:
	def __init__(self,cacheLinesPrimary,cacheLinesSecondary,blockSize):
		self.cacheLinesPrimary = cacheLinesPrimary
		self.cacheLinesSecondary = cacheLinesSecondary
		self.blockSize = blockSize
		self.crntCacheSizePrimary = 0
		self.crntCacheSizeSecondary = 0
		self.cachePrimary = {}
		self.cacheSecondary = {}

	#Function to check if block is present in primary cache
	def isInPrimaryCache(self,blockTagPrimary,dictIndexPrimary):

		if(dictIndexPrimary in self.cachePrimary.keys()):
			if(self.cachePrimary[dictIndexPrimary].blockTag == blockTagPrimary):
				return True
		return False

	#Function to check if the block is in Secondary cache
	def isInSecondaryCache(self,blockTagSecondary,dictIndexSecondary):
		if(dictIndexSecondary in self.cacheSecondary.keys()):
			if(self.cacheSecondary[dictIndexSecondary].blockTag == blockTagSecondary):
				return True
		return False

	#Function to check if index is in primary cache
	def isIndexInPrimaryCache(self,dictIndexPrimary):
		if(dictIndexPrimary in self.cachePrimary.keys()):
			return True
		return False

	#Function to check if the index is in secondary cache
	def isIndexInSecondaryCache(self,dictIndexSecondary):
		if(dictIndexSecondary in self.cacheSecondary.keys()):
			return True
		return False

	#Function to write to cache
	def writeToCache(self,memoryObj,blockTagPrimary,blockTagSecondary):
		dictIndexPrimary = int(memoryObj.memoryAddress/self.blockSize)
		dictIndexPrimary = int(dictIndexPrimary%self.cacheLinesPrimary)

		dictIndexSecondary = int(memoryObj.memoryAddress/self.blockSize)
		dictIndexSecondary = int(dictIndexSecondary%self.cacheLinesSecondary)

		if(len(self.cachePrimary) == 0):
			cprint("Cache tag Miss in primary cache","yellow")
			cprint("Cache tag Miss in secondary cache","yellow")
			self.crntCacheSizePrimary += 1
			tmpBlock = Block(blockTagPrimary)
			tmpBlock.insertInMemoryArray(memoryObj)
			self.cachePrimary[dictIndexPrimary] = tmpBlock
			return

		if(self.isInPrimaryCache(blockTagPrimary,dictIndexPrimary) == True):
			cprint("Cache tag hit in primary cache","green")
			cprint("Cache tag miss in secondary cache","yellow")
			found = self.cachePrimary[dictIndexPrimary].isInBlock(memoryObj)

			if(found == True):
				self.cachePrimary[dictIndexPrimary].updateInMemoryArray(memoryObj)
			else:
				self.cachePrimary[dictIndexPrimary].insertInMemoryArray(memoryObj)

		elif(self.isInPrimaryCache(blockTagPrimary,dictIndexPrimary) == False and self.isInSecondaryCache(blockTagSecondary,dictIndexSecondary) == False):
			cprint("Cache tag Miss in primary cache","yellow")
			cprint("Cache tag Miss in secondary cache","yellow")
			tmpBlock = Block(blockTagPrimary)
			tmpBlock.insertInMemoryArray(memoryObj)

			if(self.isIndexInPrimaryCache(dictIndexPrimary) == False):
				self.cachePrimary[dictIndexPrimary] = tmpBlock

			else:
				tmpPrimaryDeleteObj = self.cachePrimary[dictIndexPrimary]
				cprint("replacing the value of "+str(dictIndexPrimary)+" in the primary cache with new memory block "+str(blockTagPrimary),"yellow")
				cprint("Contents that are replaced are: ","yellow")
				tmpPrimaryDeleteObj.printBlock()
				print()
				self.cachePrimary[dictIndexPrimary] = tmpBlock

				tmpBlockAddress = tmpPrimaryDeleteObj.blockTag
				tmpSecondaryIndex = int(tmpBlockAddress%self.cacheLinesSecondary)

				if(self.isIndexInSecondaryCache(tmpSecondaryIndex) == False):
					self.cacheSecondary[tmpSecondaryIndex] = tmpPrimaryDeleteObj
				else:
					cprint("replacing the value of "+str(tmpSecondaryIndex)+" in the secondary cache with new memory block "+str(tmpBlockAddress),"yellow")
					cprint("Contents that are replaced are: ","yellow")
					self.cacheSecondary[tmpSecondaryIndex].printBlock()
					print()
					self.cacheSecondary[tmpSecondaryIndex] = tmpPrimaryDeleteObj

		elif(self.isInPrimaryCache(blockTagPrimary,dictIndexPrimary) == False and self.isInSecondaryCache(blockTagSecondary,dictIndexSecondary) == True):
			cprint("Cache tag Miss in primary cache","yellow")
			cprint("Cache tag Hit in secondary cache","green")
			tmpPoppedSecondBlock = self.cacheSecondary.pop(dictIndexSecondary)
			tmpPrimaryIndex = int(tmpPoppedSecondBlock.blockTag%self.cacheLinesPrimary)

			
			
			tmpBlock = tmpPoppedSecondBlock
			tmpBlock.insertInMemoryArray(memoryObj)

			if(self.isIndexInPrimaryCache(tmpPrimaryIndex) == False) :
				self.cachePrimary[tmpPrimaryIndex] = tmpBlock
			
			else:
				tmpPrimaryDeleteObj = self.cachePrimary[tmpPrimaryIndex]
				cprint("replacing the value of "+str(tmpPrimaryIndex)+" in the primary cache with new memory block "+str(tmpBlock.blockTag),"yellow")
				cprint("Contents that are replaced are: ","yellow")
				tmpPrimaryDeleteObj.printBlock()
				
				self.cachePrimary[tmpPrimaryIndex] = tmpBlock

				tmpSecondaryIndex = int(tmpPrimaryDeleteObj.blockTag%self.cacheLinesSecondary)

				if(self.isIndexInSecondaryCache(tmpSecondaryIndex) == False):
					self.cacheSecondary[tmpSecondaryIndex] = tmpPrimaryDeleteObj
				
				else:
					cprint("replacing the value of "+str(tmpSecondaryIndex)+" in the secondary cache with new memory block "+str(tmpPrimaryDeleteObj.blockTag),"yellow")
					cprint("Contents that are replaced are: ","yellow")
					self.cacheSecondary[tmpSecondaryIndex].printBlock()

					self.cacheSecondary[tmpSecondaryIndex] = tmpPrimaryDeleteObj

	#Function to read from cache
	def readCache(self,memoryObj,blockTagPrimary,blockTagSecondary):
		if(len(self.cachePrimary) == 0):
			cprint("Cache is empty","yellow")
			return

		dictIndexPrimary = int(memoryObj.memoryAddress/self.blockSize)
		dictIndexPrimary = int(dictIndexPrimary%self.cacheLinesPrimary)

		dictIndexSecondary = int(memoryObj.memoryAddress/self.blockSize)
		dictIndexSecondary = int(dictIndexSecondary%self.cacheLinesSecondary)

		if(self.isInPrimaryCache(blockTagPrimary,dictIndexPrimary) == True):
			cprint("Cache tag hit in primary cache","green")
			cprint("Cache tag miss in secondary cache","yellow")
			print("The value at the location "+str(memoryObj.memoryAddress)+" is "+str(self.cachePrimary[dictIndexPrimary].getFromBlock(memoryObj).memoryVal))

		elif(self.isInPrimaryCache(blockTagPrimary,dictIndexPrimary) == False and self.isInSecondaryCache(blockTagSecondary,dictIndexSecondary) == False):
			cprint("The memory block doesn't exists","yellow")

		elif(self.isInPrimaryCache(blockTagPrimary,dictIndexPrimary) == False and self.isInSecondaryCache(blockTagSecondary,dictIndexSecondary) == True):
			cprint("cache tag miss is primary cache","yellow")
			tmpPoppedSecondBlock = self.cacheSecondary.pop(dictIndexSecondary)
			tmpPrimaryIndex = int(tmpPoppedSecondBlock.blockTag%self.cacheLinesPrimary)
			tmpBlock = tmpPoppedSecondBlock
			cprint("cache tag hit is secondary cache","green")
			if(tmpBlock.isInBlock(memoryObj) == False):
				cprint("The address doesn't exists","yellow")
				return
			else:
				print("The value at location "+str(memoryObj.memoryAddress)+" is "+str(tmpBlock.getFromBlock(memoryObj).memoryVal))

			if(self.isIndexInPrimaryCache(tmpPrimaryIndex) == False) :
				self.cachePrimary[tmpPrimaryIndex] = tmpBlock

			else:
				tmpPrimaryDeleteObj = self.cachePrimary[tmpPrimaryIndex]
				cprint("replacing the value of "+str(tmpPrimaryIndex)+" in the primary cache with new memory block "+str(tmpBlock.blockTag),"yellow")
				cprint("Contents that are replaced are: ","yellow")
				tmpPrimaryDeleteObj.printBlock()
				
				self.cachePrimary[tmpPrimaryIndex] = tmpBlock
				tmpSecondaryIndex = int(tmpPrimaryDeleteObj.blockTag%self.cacheLinesSecondary)

				if(self.isIndexInSecondaryCache(tmpSecondaryIndex) == False):
					self.cacheSecondary[tmpSecondaryIndex] = tmpPrimaryDeleteObj
				
				else:
					cprint("replacing the value of "+str(tmpSecondaryIndex)+" in the secondary cache with new memory block "+str(tmpPrimaryDeleteObj.blockTag),"yellow")
					cprint("Contents that are replaced are: ","yellow")
					self.cacheSecondary[tmpSecondaryIndex].printBlock()
					self.cacheSecondary[tmpSecondaryIndex] = tmpPrimaryDeleteObj

	#Function to print primary cache
	def printPrimaryCache(self):
		if(len(self.cachePrimary) == 0):
			cprint("Primary Cache is empty","yellow")
			return
		cprint("Primary cache:","cyan")
		print()
		count = 1
		tmpKeyLst = self.cachePrimary.keys()
		tmpKeyLst = list(tmpKeyLst)
		tmpKeyLst.sort()
		for val in tmpKeyLst:
			tmpStr = "Cache Line: "+str(int(int(self.cachePrimary[val].blockTag%self.cacheLinesPrimary)))
			cprint(tmpStr,"white","on_blue",attrs=["bold"])
			count += 1
			self.cachePrimary[val].printBlock();

	#Function to print Secondary cache
	def printSecondaryCache(self):
		if(len(self.cacheSecondary) == 0):
			cprint("Secondary Cache is empty","yellow")
			return
		print()
		cprint("Secondary cache","cyan")
		tmpKeyLst = self.cacheSecondary.keys()
		tmpKeyLst = list(tmpKeyLst)
		tmpKeyLst.sort()
		count = 1
		for val in tmpKeyLst:
			tmpStr = "Cache Line: "+str(int(int(self.cacheSecondary[val].blockTag%self.cacheLinesSecondary)))
			cprint(tmpStr,"white","on_blue",attrs=["bold"])
			count += 1
			self.cacheSecondary[val].printBlock();

	#Function to print both cache
	def printCache(self):
		if(len(self.cachePrimary) == 0):
			cprint("Primary Cache is empty","yellow")
			return

		print()
		cprint("Primary cache","cyan")
		tmpKeyLst = self.cachePrimary.keys()
		tmpKeyLst = list(tmpKeyLst)
		tmpKeyLst.sort()
		count = 1;
		for val in tmpKeyLst:
			tmpStr = "Cache Line: "+str(int(int(self.cachePrimary[val].blockTag%self.cacheLinesPrimary)))
			cprint(tmpStr,"white","on_blue",attrs=["bold"])
			count += 1
			self.cachePrimary[val].printBlock();

		print()
		print()
		print()

		if(len(self.cacheSecondary) == 0):
			cprint("Secondary Cache is empty","yellow")
			return

		cprint("Secondary cache","cyan")
		tmpKeyLst = self.cacheSecondary.keys()
		tmpKeyLst = list(tmpKeyLst)
		tmpKeyLst.sort()
		count = 1
		for val in tmpKeyLst:
			tmpStr = "Cache Line: "+str(int(int(self.cacheSecondary[val].blockTag%self.cacheLinesSecondary)))
			cprint(tmpStr,"white","on_blue",attrs=["bold"])
			count += 1
			self.cacheSecondary[val].printBlock();

class SetObject:
	def __init__(self,cacheLines,blockSize,cacheName):
		self.cacheLines = cacheLines
		self.blockSize = blockSize
		self.setSize = self.cacheLines*self.blockSize
		self.LocalTimeChecking = []
		self.crntCacheSize = 0
		self.setCache ={}
		self.cacheName = cacheName

	def isInCache(self,blockTag):
		if(self.crntCacheSize == 0):
			return False
		for val in self.setCache:
			if(val == blockTag):
				return True
		return False
	
	def updateLocalTimeCheckingArr(self,blockTag):
		for val in self.LocalTimeChecking:
			if(val == blockTag):
				self.LocalTimeChecking.remove(val)
				break
		self.LocalTimeChecking.append(blockTag)

	def writeInSetCache(self,memoryObj,blockTag):

		if(len(self.setCache) == 0):
			cprint("Cache tag miss in "+str(self.cacheName),"yellow")
			self.crntCacheSize += 1
			tmpBlock = Block(blockTag)
			tmpBlock.insertInMemoryArray(memoryObj)
			self.setCache[blockTag] = tmpBlock
			self.LocalTimeChecking.append(blockTag)

		elif(self.isInCache(blockTag) == True):
			cprint("Cache Hit in "+str(self.cacheName),"green")
			for val in self.setCache:
				if(val == blockTag):
					if(self.setCache[val].isInBlock(memoryObj) == True):
						self.setCache[val].updateInMemoryArray(memoryObj)
					else:
						self.setCache[val].insertInMemoryArray(memoryObj)
					break
			self.updateLocalTimeCheckingArr(blockTag)

		elif(self.isInCache(blockTag) == False):
			cprint("Cache tag miss "+str(self.cacheName),"yellow")

			tmpBlock = Block(blockTag)
			tmpBlock.insertInMemoryArray(memoryObj)

			if(self.crntCacheSize < self.cacheLines):
				self.setCache[blockTag] = tmpBlock
				self.crntCacheSize += 1

			else:
				cprint("Currently cache set is full so applying LRU policy in the set to pop element in "+str(self.cacheName),"yellow")
				cprint("The block popped is: "+str(self.LocalTimeChecking[0]),"yellow")
				cprint("contents:","yellow")
				self.setCache[self.LocalTimeChecking[0]].printBlock()

				tmpPoppedBlockTag = self.LocalTimeChecking.pop(0)
				deletedBlock = 0
				for val in self.setCache:
					if(val == tmpPoppedBlockTag):
						deletedBlock = self.setCache.pop(val)
						break
				self.setCache[blockTag] = tmpBlock
			
			self.LocalTimeChecking.append(blockTag)

#class to implement set associative mapping
class SetAssociative:
	def __init__(self,cacheLinesPrimary,cacheLinesSecondary,blockSize,k):
		self.cacheLinesPrimary = cacheLinesPrimary
		self.cacheLinesSecondary = cacheLinesSecondary
		self.blockSize = blockSize
		self.k = k
		self.numberOfSetsPrimary = int(self.cacheLinesPrimary/self.k)
		self.numberOfSetsSecondary = int(self.cacheLinesSecondary/self.k)
		self.crntSetCountPrimary = 0
		self.crntSetCountSecondary = 0
		self.cacheLinesPrimarySet = int(self.cacheLinesPrimary/self.numberOfSetsPrimary)
		self.cacheLinesSecondarySet = int(self.cacheLinesSecondary/self.numberOfSetsSecondary)
		self.cachePrimary = {}
		self.cacheSecondary = {}

	#Function to check if the block is in primary cache
	def isBlockInPrimaryCache(self,blockTag,setNum):
		ind = 0
		if(setNum in self.cachePrimary.keys()):
			tmpLst = self.cachePrimary[setNum]
			for val in tmpLst:
				if(val.blockTag == blockTag):
					return ind
				ind += 1
		return -1
	#Function to check if the block is in secondary cache
	def isBlockInSecondaryCache(self,blockTag,setNum):
		ind = 0
		if(setNum in self.cacheSecondary.keys()):
			tmpLst = self.cacheSecondary[setNum]
			for val in tmpLst:
				if(val.blockTag == blockTag):
					return ind
				ind += 1
		return -1
	#function to arrange in secondary cache
	def arrangeInSecondaryCache(self,blockObj,setNum):
		if(setNum in self.cacheSecondary.keys()):
			tmpLst = self.cacheSecondary[setNum]

			if(len(tmpLst) < self.cacheLinesSecondarySet):
				tmpLst.append(blockObj)
			else:
				tmpPoppedBlock = tmpLst.pop(0)
				cprint("Currently cache set is full so applying LRU policy in the set to pop element in secondary cache","yellow")
				cprint("element popped is:")
				tmpPoppedBlock.printBlock()
				print()
				print()
				tmpLst.append(blockObj)

			self.cacheSecondary[setNum] = tmpLst
		else:
			tmpLst = []
			tmpLst.append(blockObj)
			self.cacheSecondary[setNum] = tmpLst
	
	#Function to write to cache
	def writeToCache(self,memoryObj,blockTagPrimary,blockTagSecondary):
		setNumPrimary = int(blockTagPrimary%self.numberOfSetsPrimary)
		setNumSecondary = int(blockTagSecondary%self.numberOfSetsSecondary)

		if(setNumPrimary not in self.cachePrimary.keys()):
			cprint("cache miss in primary cache","yellow")
			cprint("cache miss in secondary cache","yellow")
			print()
			tmpLst = []
			tmpBlock = Block(blockTagPrimary)
			tmpBlock.insertInMemoryArray(memoryObj)
			tmpLst.append(tmpBlock)
			self.cachePrimary[setNumPrimary] = tmpLst
			return
		
		primaryIndexInSet = self.isBlockInPrimaryCache(blockTagPrimary,setNumPrimary)
		secondaryIndexInSet = self.isBlockInSecondaryCache(blockTagSecondary,setNumSecondary)

		if(primaryIndexInSet != -1):
			cprint("Cache hit in primary cache","green")
			cprint("Cache miss in secondary cache","yellow")
			tmpObjPopped = self.cachePrimary[setNumPrimary].pop(primaryIndexInSet)
			
			if(tmpObjPopped.isInBlock(memoryObj) == False):
				tmpObjPopped.insertInMemoryArray(memoryObj)
			else:
				tmpObjPopped.updateInMemoryArray(memoryObj)

			self.cachePrimary[setNumPrimary].append(tmpObjPopped)

		elif(primaryIndexInSet == -1 and secondaryIndexInSet != -1):
			cprint("Cache miss in primary cache","yellow")
			cprint("Cache hit in secondary cache","green")
			print()
			tmpPoppedObjSecondary = self.cacheSecondary[setNumSecondary].pop(secondaryIndexInSet)
			if(tmpPoppedObjSecondary.isInBlock(memoryObj) == True):
				tmpPoppedObjSecondary.updateInMemoryArray(memoryObj)
			else:
				tmpPoppedObjSecondary.insertInMemoryArray(memoryObj)
			
			primarySetIndexPoppedElement = int(tmpPoppedObjSecondary.blockTag%self.numberOfSetsPrimary)

			if(primarySetIndexPoppedElement in self.cachePrimary.keys()):
				tmpLst = []
				tmpLst = self.cachePrimary[primarySetIndexPoppedElement]
				if(len(tmpLst)<self.cacheLinesPrimarySet):
					tmpLst.append(tmpPoppedObjSecondary)
				else:
					cprint("Currently cache set is full so applying LRU policy in the set to pop element in primary cache","yellow")
					cprint("element popped is:")
					tmpPoppedBlock = tmpLst.pop(0)
					tmpPoppedBlock.printBlock()
					print()
					print()
					tmpLst.append(tmpPoppedObjSecondary)
					self.arrangeInSecondaryCache(tmpPoppedBlock,int(tmpPoppedBlock.blockTag%self.numberOfSetsSecondary))
				self.cachePrimary[primarySetIndexPoppedElement] = tmpLst
			else:
				tmpLst = []
				tmpLst.append(tmpPoppedObjSecondary)
				self.cachePrimary[primarySetIndexPoppedElement] = tmpLst
		
		elif(primaryIndexInSet == -1 and secondaryIndexInSet == -1):
			cprint("Cache miss in primary cache","yellow")
			cprint("Cache miss in secondary cache","yellow")

			if(setNumPrimary not in self.cachePrimary):
				tmpBlock = Block(blockTagPrimary)
				tmpBlock.insertInMemoryArray(memoryObj)
				tmpLst = []
				tmpLst.append(tmpBlock)
				self.cachePrimary[setNumPrimary] = tmpLst

			else:
				tmpBlock = Block(blockTagPrimary)
				tmpBlock.insertInMemoryArray(memoryObj)

				tmpLst = self.cachePrimary[setNumPrimary]
				if(len(tmpLst) < self.cacheLinesPrimarySet):
					tmpLst.append(tmpBlock)
					self.cachePrimary[setNumPrimary] = tmpLst
				else:
					cprint("Currently cache set is full so applying LRU policy in the set to pop element in primary cache","yellow")
					cprint("element popped is:")
					tmpPoppedBlockObj = self.cachePrimary[setNumPrimary].pop(0)
					tmpPoppedBlockObj.printBlock()
					print()
					print()
					tmpLst.append(tmpBlock)
					self.arrangeInSecondaryCache(tmpPoppedBlockObj,int(tmpPoppedBlockObj.blockTag%self.numberOfSetsSecondary))
					self.cachePrimary[setNumPrimary] = tmpLst

	#Function to read from cache
	def readCache(self,memoryObj,blockTagPrimary,blockTagSecondary):
		if(len(self.cachePrimary) == 0):
			cprint("Primary cache is empty","yellow")
			return

		setNumPrimary = int(blockTagPrimary%self.numberOfSetsPrimary)
		setNumSecondary = int(blockTagSecondary%self.numberOfSetsSecondary)

		if(setNumPrimary not in self.cachePrimary.keys()):
			cprint("The memory block doesn't exists","yellow")
			return

		primaryIndexInSet = self.isBlockInPrimaryCache(blockTagPrimary,setNumPrimary)
		secondaryIndexInSet = self.isBlockInSecondaryCache(blockTagSecondary,setNumSecondary)

		if(primaryIndexInSet != -1):
			
			if(self.cachePrimary[setNumPrimary][primaryIndexInSet].isInBlock(memoryObj) == False):
				cprint("The memory object doesn't exists")
			
			else:
				tmpObjPopped = self.cachePrimary[setNumPrimary].pop(primaryIndexInSet)
				cprint("Cache hit in primary cache","green")
				cprint("Cache miss in primary cache","yellow")
				print("The value at the location "+str(memoryObj.memoryAddress)+" is "+str(tmpObjPopped.getFromBlock(memoryObj).memoryVal))
				self.cachePrimary[setNumPrimary].append(tmpObjPopped)

		elif(primaryIndexInSet == -1 and secondaryIndexInSet != -1):
			cprint("Cache miss in primary cache","yellow")
			cprint("Cache hit in secondary cache","green")
			tmp = self.cacheSecondary[setNumSecondary][secondaryIndexInSet]
			if(tmp.isInBlock(memoryObj) == False):
				cprint("The address doesn't exists","yellow")
				return

			tmpPoppedObjSecondary = self.cacheSecondary[setNumSecondary].pop(secondaryIndexInSet)
			print("The value at the address "+str(memoryObj.memoryAddress) + " is "+str(tmpPoppedObjSecondary.getFromBlock(memoryObj).memoryVal))
			
			primarySetIndexPoppedElement = int(tmpPoppedObjSecondary.blockTag%self.numberOfSetsPrimary)

			if(primarySetIndexPoppedElement in self.cachePrimary.keys()):
				tmpLst = []
				tmpLst = self.cachePrimary[primarySetIndexPoppedElement]
				if(len(tmpLst)<self.cacheLinesPrimarySet):
					tmpLst.append(tmpPoppedObjSecondary)
				else:
					cprint("Currently cache set is full so applying LRU policy in the set to pop element in primary cache","yellow")
					cprint("element popped is:")
					tmpPoppedBlock = tmpLst.pop(0)
					tmpPoppedBlock.printBlock()
					print()
					print()
					tmpLst.append(tmpPoppedObjSecondary)
					self.arrangeInSecondaryCache(tmpPoppedBlock,int(tmpPoppedBlock.blockTag%self.numberOfSetsSecondary))
				self.cachePrimary[primarySetIndexPoppedElement] = tmpLst
			else:
				tmpLst = []
				tmpLst.append(tmpPoppedObjSecondary)
				self.cachePrimary[primarySetIndexPoppedElement] = tmpLst
		else:
			cprint("The address doesn't exists","yellow")

	#Function to print from primary cache
	def printPrimaryCache(self):
		if(len(self.cachePrimary) == 0):
			cprint("Primary cache is empty","yellow")
			return
		cprint("Primary cache","cyan")
		print()
		for val in self.cachePrimary:
			cprint("The set number is: "+str(val),"white","on_magenta",attrs = ["bold"])
			for val2 in self.cachePrimary[val]:
				val2.printBlock()
			print()

	#Function to print from secondary cache
	def printSecondaryCache(self):
		if(len(self.cacheSecondary) == 0):
			cprint("Secondary cache is empty","yellow")
			return
		cprint("Secondary cache","cyan")
		for val in self.cacheSecondary:
			cprint("The set number is: "+str(val),"white","on_magenta",attrs = ["bold"])
			for val2 in self.cacheSecondary[val]:
				val2.printBlock()
			print()

	#Function to print both cache
	def printCache(self):
		if(len(self.cachePrimary) == 0):
			cprint("Primary cache is empty","yellow")
			return
			
		cprint("Primary cache","cyan")
		print()
		for val in self.cachePrimary:
			cprint("The set number is: "+str(val),"white","on_magenta",attrs = ["bold"])
			for val2 in self.cachePrimary[val]:
				val2.printBlock()
			print()

		print()
		print()
		print()
		if(len(self.cacheSecondary) == 0):
			cprint("Secondary cache is empty","yellow")
			return
		cprint("Secondary cache","cyan")
		for val in self.cacheSecondary:
			cprint("The set number is: "+str(val),"white","on_magenta",attrs = ["bold"])
			for val2 in self.cacheSecondary[val]:
				val2.printBlock()
			print()

#Main Function to which collaborats all the classes together
def Main():

	cprint("Type of mapping: ","white","on_yellow",attrs=["bold","dark"])
	print("1. Direct Mapping")
	print("2. Fully Associative")
	print("3. Set Associative")
	mapping = input()
	mapping = mapping.lower()
	print()

	while(True):
		print("Enter the number of cache lines:",end=" ")
		cacheLinesInp = int(input())
		if(is2Power(cacheLinesInp) == False):
			cprint("Invalid input of cache line","red")
			cprint("try again","red")
			continue
		print("Enter the block size:",end=" ")
		blockSizeInp = int(input())
		if(is2Power(blockSizeInp) == False):
			cprint("Invalid input of block size","red")
			cprint("try again","red")
			continue
		break

	print()
	print()
	cacheLinesPrimary = int(cacheLinesInp/2)

	cprint("CACHE LINES PRIMARY: "+str(cacheLinesInp),"white","on_green",attrs=["bold"])
	cprint("CACHE LINES SECONDARY: "+str(int(cacheLinesInp/2)),"white","on_green",attrs=["bold"])
	cprint("BLOCK SIZE:  "+str(blockSizeInp),"white","on_green",attrs=["bold"])
	cprint("MAPPING:  "+str(mapping.upper()),"white","on_green",attrs=["bold"])

	if(mapping  == "direct mapping"):
		myCache =  DirectMapping(cacheLinesPrimary,cacheLinesInp,blockSizeInp)
	elif(mapping == "fully associative"):
		myCache = FullyAssociative(cacheLinesPrimary,cacheLinesInp,blockSizeInp)
	elif(mapping == "set associative"):
		while(True):
			print("enter the value of k for k way set associative mapping")
			k = int(input())
			if(is2Power(k) == False):
				cprint("Invalid input of k","red")
				cprint("try again","red")
				continue
			myCache = SetAssociative(cacheLinesPrimary,cacheLinesInp,blockSizeInp,k)
			break


	print()
	while(True):
		cprint("ENTER THE OPERATION","white","on_red",attrs=["bold"])
		print("1. WRITE (ADDRESS) (VALUE)")
		print("2. READ (ADDRESS)")
		print("3. CACHE ")
		print("4. CACHE PRIMARY")
		print("5. CACHE SECONDARY")
		print("4. CLEAR")
		print("5. EXIT")
		inp = input()
		inp = inp.upper()
		print()

		if(inp == "EXIT"):
			break
		elif(inp == "CLEAR"):
			system("cls")
		elif(inp == "CACHE"):
			myCache.printCache()
		elif(inp == "CACHE PRIMARY"):
			myCache.printPrimaryCache()
		elif(inp == "CACHE SECONDARY"):
			myCache.printSecondaryCache()
		else:
			inpLst = []
			inpLst = inp.split(" ")

			if(len(inpLst) == 3):
				x=int(inpLst[1])
				y=int(inpLst[2])
				tmpMemoryObj = Memory(y,x,int(x/blockSizeInp),int(x%blockSizeInp))
				myCache.writeToCache(tmpMemoryObj,int(x/blockSizeInp),int(x/blockSizeInp))
			
			elif(len(inpLst) == 2):
				x = int(inpLst[1])
				tmpMemoryObj = Memory(-1,x,int(x/blockSizeInp),int(x%blockSizeInp))
				myCache.readCache(tmpMemoryObj,int(x/blockSizeInp),int(x/blockSizeInp))
		input()

Main()