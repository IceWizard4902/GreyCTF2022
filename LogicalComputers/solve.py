import torch

def tensorize(s : str) -> torch.Tensor:
  return torch.Tensor([(1 if (ch >> i) & 1 == 1 else -1) for ch in list(map(ord, s)) for i in range(8)])

class NeuralNetwork(torch.nn.Module):
  def __init__(self, in_dimension, mid_dimension, out_dimension=1):
    super(NeuralNetwork, self).__init__()
    self.layer1 = torch.nn.Linear(in_dimension, mid_dimension)
    self.layer2 = torch.nn.Linear(mid_dimension, out_dimension)

  def step_activation(self, x : torch.Tensor) -> torch.Tensor:
    x[x <= 0] = -1
    x[x >  0] = 1
    return x

  def forward(self, x : torch.Tensor) -> int:
    x = self.layer1(x)
    x = self.step_activation(x)
    x = self.layer2(x)
    return int(x)

flag = "grey{~~~~~~~~~~~~~~}"
in_data = tensorize(flag)
in_dim	= len(in_data)

model = NeuralNetwork(in_dim, 1280)
model.load_state_dict(torch.load("model.pth"))

def get_flag(flag):
  best_score = model(tensorize(flag))
  best_candidate = flag
  for i in range(5, len(flag) - 1):
    for j in range(33, 127):
      temp = best_candidate[:i] + str(chr(j)) + best_candidate[i + 1:]
      score = model(tensorize(temp))
      if score > best_score:
        best_score = score 
        best_candidate = temp
  return best_candidate

print(get_flag(flag))