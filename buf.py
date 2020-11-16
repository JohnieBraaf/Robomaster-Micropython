class FrameBuffer(object):
    def __init__(self, size):
        self.size = size
        self.overflow = 0
        self.index_put = 0
        self.index_get = 0
        self.next_index = 0

        # dummy frames to pass as reference when buffer is full or empty
        self.empty_get_bytes = bytearray(8)
        self.empty_get_frame = [0, 0, 0, memoryview(self.empty_get_bytes)]
        self.empty_put_bytes = bytearray(8)
        self.empty_put_frame = [0, 0, 0, memoryview(self.empty_put_bytes)]
        
        # allocate byte arrays
        self.data = []
        for i in range(size):
            self.data.append(bytearray(8))

        # allocate frames with references to the byte arrays
        self.frame = []
        for i in range(size):
            self.frame.append([i, 0, 0, memoryview(self.data[i])])
    
    @micropython.native
    def put(self):
        self.next_index = (self.index_put + 1) % self.size
        if self.index_get != self.next_index:
            self.index_put = self.next_index
            return self.frame[self.index_put]
        else:
            self.overflow += 1
            return self.empty_put_frame # buffer overflow

    @micropython.native
    def get(self):
        if self.index_get != self.index_put:
            self.index_get = (self.index_get + 1) % self.size
            return self.frame[self.index_get]
        else:
            return self.empty_get_frame  # buffer empty

class RingBuffer:
    def __init__(self, size):
        self.size = size + 1
        self.data = bytearray(self.size)
        self.index_put = 0
        self.index_get = 0
        self.count = 0
    
    @micropython.native
    def any(self):
        if self.index_get != self.index_put:
            return True
        return False

    @micropython.native
    def put(self, value):
        next_index = (self.index_put + 1) % self.size
        
        if self.index_get != next_index: 
            self.data[self.index_put] = value
            self.index_put = next_index
            self.count += 1
            return value
        else:
            print("overflow")
            return None  # buffer full
    
    @micropython.native
    def get(self):
        if self.any():
            value = self.data[self.index_get]
            self.index_get = (self.index_get + 1) % self.size
            self.count -= 1
            return value
        else:
            return None  # buffer empty
        