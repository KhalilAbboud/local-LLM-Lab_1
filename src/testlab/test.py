import torch

x = torch.randn(4, 3)
mu = x.mean(dim=0)

x_norm = (x - mu) / x.std(dim=0)

print("Original tensor:")
print(x)

print("Mean of each column:")
print(mu)

print("Normalized tensor:")
print(x_norm)