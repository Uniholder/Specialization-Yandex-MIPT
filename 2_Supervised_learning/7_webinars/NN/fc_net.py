from builtins import range
from builtins import object
import numpy as np

from cs231n.layers import *
from cs231n.layer_utils import *


def affine_bn_relu_forward(x, w, b, gamma, beta, bn_param):
    a, fc_cache = affine_forward(x, w, b)
    bn_a, bn_cache = batchnorm_forward(a, gamma, beta, bn_param)
    out, relu_cache = relu_forward(bn_a)
    cache = (fc_cache, bn_cache, relu_cache)
    return out, cache

def affine_bn_relu_backward(dout, cache):
    fc_cache, bn_cache, relu_cache = cache
    da = relu_backward(dout, relu_cache)
    da_bn, dgamma, dbeta = batchnorm_backward(da, bn_cache)
    dx, dw, db = affine_backward(da_bn, fc_cache)
    return dx, dw, db, dgamma, dbeta

def affine_ln_relu_forward(x, w, b, gamma, beta, bn_param):
    a, fc_cache = affine_forward(x, w, b)
    bn_a, bn_cache = layernorm_forward(a, gamma, beta, bn_param)
    out, relu_cache = relu_forward(bn_a)
    cache = (fc_cache, bn_cache, relu_cache)
    return out, cache

def affine_ln_relu_backward(dout, cache):
    fc_cache, bn_cache, relu_cache = cache
    da = relu_backward(dout, relu_cache)
    da_bn, dgamma, dbeta = layernorm_backward(da, bn_cache)
    dx, dw, db = affine_backward(da_bn, fc_cache)
    return dx, dw, db, dgamma, dbeta


class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network with ReLU nonlinearity and
    softmax loss that uses a modular layer design. We assume an input dimension
    of D, a hidden dimension of H, and perform classification over C classes.

    The architecure should be affine - relu - affine - softmax.

    Note that this class does not implement gradient descent; instead, it
    will interact with a separate Solver object that is responsible for running
    optimization.

    The learnable parameters of the model are stored in the dictionary
    self.params that maps parameter names to numpy arrays.
    """

    def __init__(self, input_dim=3*32*32, hidden_dim=100, num_classes=10,
                 weight_scale=1e-3, reg=0.0):
        """
        Initialize a new network.

        Inputs:
        - input_dim: An integer giving the size of the input
        - hidden_dim: An integer giving the size of the hidden layer
        - num_classes: An integer giving the number of classes to classify
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - reg: Scalar giving L2 regularization strength.
        """
        self.params = {}
        self.reg = reg

        ############################################################################
        # TODO: Initialize the weights and biases of the two-layer net. Weights    #
        # should be initialized from a Gaussian centered at 0.0 with               #
        # standard deviation equal to weight_scale, and biases should be           #
        # initialized to zero. All weights and biases should be stored in the      #
        # dictionary self.params, with first layer weights                         #
        # and biases using the keys 'W1' and 'b1' and second layer                 #
        # weights and biases using the keys 'W2' and 'b2'.                         #
        ############################################################################
        self.params['W1'] = np.random.normal(size=(input_dim, hidden_dim), scale=weight_scale)
        #print(self.params['W1'])
        self.params['b1'] = np.zeros(hidden_dim)
        self.params['W2'] = np.random.normal(size=(hidden_dim, num_classes), scale=weight_scale)
        self.params['b2'] = np.zeros(num_classes)
        self.num_layers = 2
        self.layers = []
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

    def stable_softmax(self, z):
        e_x = np.exp(z)
        a = e_x / np.sum(e_x, axis=1, keepdims=True)
        return a

    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.

        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
          names to gradients of the loss with respect to those parameters.
        """
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the two-layer net, computing the    #
        # class scores for X and storing them in the scores variable.              #
        ############################################################################
        current = X
        reg_loss = 0
        self.layers = []
        self.layers.append(('first', X))
        for i in range(1, self.num_layers):
            Wi = self.params['W{}'.format(i)]
            bi = self.params['b{}'.format(i)]
            reg_loss += 0.5 * self.reg * np.sum(Wi*Wi)
            #print(reg_loss)
            current, cache = affine_relu_forward(current, Wi, bi)
            self.layers.append(("relu", cache))
        Wi = self.params['W{}'.format(self.num_layers)]
        bi = self.params['b{}'.format(self.num_layers)]
        reg_loss += 0.5 * self.reg * np.sum(Wi*Wi)
        current, cache = affine_forward(current, Wi, bi)
        self.layers.append(("last", cache))
        scores = current
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If y is None then we are in test mode so just return scores
        if y is None:
            return scores

        loss, grads = 0, {}
        ############################################################################
        # TODO: Implement the backward pass for the two-layer net. Store the loss  #
        # in the loss variable and gradients in the grads dictionary. Compute data #
        # loss using softmax, and make sure that grads[k] holds the gradients for  #
        # self.params[k]. Don't forget to add L2 regularization!                   #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        loss, dx = softmax_loss(scores, y)
        loss += reg_loss
        for i in range(len(self.layers) -1, -1, -1):
            (name, value) = self.layers[i]
            if name=='last':
                dx, dw, db = affine_backward(dx, value)
                grads['W{}'.format(i)] = dw + self.reg * self.params['W{}'.format(i)]
                grads['b{}'.format(i)] = db
            if (name=='relu'):
                dx, dw, db = affine_relu_backward(dx, value)
                grads['W{}'.format(i)] = dw + self.reg * self.params['W{}'.format(i)]
                grads['b{}'.format(i)] = db
            if (name=='first'):
                pass
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads


class FullyConnectedNet(object):
    """
    A fully-connected neural network with an arbitrary number of hidden layers,
    ReLU nonlinearities, and a softmax loss function. This will also implement
    dropout and batch/layer normalization as options. For a network with L layers,
    the architecture will be

    {affine - [batch/layer norm] - relu - [dropout]} x (L - 1) - affine - softmax

    where batch/layer normalization and dropout are optional, and the {...} block is
    repeated L - 1 times.

    Similar to the TwoLayerNet above, learnable parameters are stored in the
    self.params dictionary and will be learned using the Solver class.
    """

    def __init__(self, hidden_dims, input_dim=3*32*32, num_classes=10,
                 dropout=1, normalization=None, reg=0.0,
                 weight_scale=1e-2, dtype=np.float32, seed=None):
        """
        Initialize a new FullyConnectedNet.

        Inputs:
        - hidden_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=1 then
          the network should not use dropout at all.
        - normalization: What type of normalization the network should use. Valid values
          are "batchnorm", "layernorm", or None for no normalization (the default).
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - dtype: A numpy datatype object; all computations will be performed using
          this datatype. float32 is faster but less accurate, so you should use
          float64 for numeric gradient checking.
        - seed: If not None, then pass this random seed to the dropout layers. This
          will make the dropout layers deteriminstic so we can gradient check the
          model.
        """
        self.normalization = normalization
        self.use_dropout = dropout != 1
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}

        ############################################################################
        # TODO: Initialize the parameters of the network, storing all values in    #
        # the self.params dictionary. Store weights and biases for the first layer #
        # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
        # initialized from a normal distribution centered at 0 with standard       #
        # deviation equal to weight_scale. Biases should be initialized to zero.   #
        #                                                                          #
        # When using batch normalization, store scale and shift parameters for the #
        # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
        # beta2, etc. Scale parameters should be initialized to ones and shift     #
        # parameters should be initialized to zeros.                               #
        ############################################################################
        self.hidden_dims = hidden_dims
        self.layers = []
        for i in range(0, self.num_layers):
            first = input_dim if i==0 else self.hidden_dims[i-1]
            last = num_classes if (i == self.num_layers - 1) else self.hidden_dims[i]
            self.params['W{}'.format(i+1)] = np.random.normal(size=(first, last), scale=weight_scale)
            self.params['b{}'.format(i+1)] = np.zeros(last)
            if ((self.normalization=='batchnorm' or self.normalization=='layernorm') and i != self.num_layers - 1):
                self.params['gamma{}'.format(i+1)] = np.ones(last)
                self.params['beta{}'.format(i+1)] = np.zeros(last)
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # When using dropout we need to pass a dropout_param dictionary to each
        # dropout layer so that the layer knows the dropout probability and the mode
        # (train / test). You can pass the same dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {'mode': 'train', 'p': dropout}
            if seed is not None:
                self.dropout_param['seed'] = seed

        # With batch normalization we need to keep track of running means and
        # variances, so we need to pass a special bn_param object to each batch
        # normalization layer. You should pass self.bn_params[0] to the forward pass
        # of the first batch normalization layer, self.bn_params[1] to the forward
        # pass of the second batch normalization layer, etc.
        self.bn_params = []
        if self.normalization=='batchnorm':
            self.bn_params = [{'mode': 'train'} for i in range(self.num_layers - 1)]
        if self.normalization=='layernorm':
            self.bn_params = [{} for i in range(self.num_layers - 1)]

        # Cast all parameters to the correct datatype
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)
        
        print(self.bn_params)

    def loss(self, X, y=None):
        """
        Compute loss and gradient for the fully-connected net.

        Input / output: Same as TwoLayerNet above.
        """
        X = X.astype(self.dtype)
        mode = 'test' if y is None else 'train'

        # Set train/test mode for batchnorm params and dropout param since they
        # behave differently during training and testing.
        if self.use_dropout:
            self.dropout_param['mode'] = mode
        if self.normalization=='batchnorm':
            for bn_param in self.bn_params:
                bn_param['mode'] = mode
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the fully-connected net, computing  #
        # the class scores for X and storing them in the scores variable.          #
        #                                                                          #
        # When using dropout, you'll need to pass self.dropout_param to each       #
        # dropout forward pass.                                                    #
        #                                                                          #
        # When using batch normalization, you'll need to pass self.bn_params[0] to #
        # the forward pass for the first batch normalization layer, pass           #
        # self.bn_params[1] to the forward pass for the second batch normalization #
        # layer, etc.                                                              #
        ############################################################################
        current = X
        reg_loss = 0
        self.layers = []
        self.masks = []
        self.layers.append(('first', X))
        for i in range(1, self.num_layers):
            Wi = self.params['W{}'.format(i)]
            bi = self.params['b{}'.format(i)]
            #print(current.shape, Wi.shape)
            reg_loss += 0.5 * self.reg * np.sum(Wi*Wi)
            #print(reg_loss)
            if (self.normalization=='batchnorm'):
                bn = self.bn_params[i-1]
                if bn['mode']=='train':
                    gamma = self.params['gamma{}'.format(i)]
                    beta = self.params['beta{}'.format(i)]
                    #print(beta.shape, Wi.shape, bn_param, bn)
                    current, cache = affine_bn_relu_forward(current, Wi, bi, gamma, beta, bn)
                    if (self.use_dropout):
                        current, drop_cache = dropout_forward(current, self.dropout_param)
                else:
                    gamma = self.params['gamma{}'.format(i)]
                    beta = self.params['beta{}'.format(i)]
                    current, cache = affine_bn_relu_forward(current, Wi, bi, gamma, beta, bn)
                    if (self.use_dropout):
                        current, drop_cache = dropout_forward(current, self.dropout_param)
            elif (self.normalization=='layernorm'):
                bn = self.bn_params[i-1]
                gamma = self.params['gamma{}'.format(i)]
                beta = self.params['beta{}'.format(i)]
                #print(beta.shape, Wi.shape, bn_param, bn)
                current, cache = affine_ln_relu_forward(current, Wi, bi, gamma, beta, bn)
                if (self.use_dropout):
                    current, drop_cache = dropout_forward(current, self.dropout_param)
            else:
                #print('here', len(self.bn_params), i)
                current, cache = affine_relu_forward(current, Wi, bi)
                if (self.use_dropout):
                    current, drop_cache = dropout_forward(current, self.dropout_param)
            if (self.use_dropout):
                self.masks.append(drop_cache)
            self.layers.append(("relu", cache))
        Wi = self.params['W{}'.format(self.num_layers)]
        bi = self.params['b{}'.format(self.num_layers)]
        reg_loss += 0.5 * self.reg * np.sum(Wi*Wi)
        current, cache = affine_forward(current, Wi, bi)
        self.layers.append(("last", cache))
        scores = current
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If test mode return early
        if mode == 'test':
            return scores

        loss, grads = 0.0, {}
        ############################################################################
        # TODO: Implement the backward pass for the fully-connected net. Store the #
        # loss in the loss variable and gradients in the grads dictionary. Compute #
        # data loss using softmax, and make sure that grads[k] holds the gradients #
        # for self.params[k]. Don't forget to add L2 regularization!               #
        #                                                                          #
        # When using batch/layer normalization, you don't need to regularize the scale   #
        # and shift parameters.                                                    #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        loss, dx = softmax_loss(scores, y)
        loss += reg_loss
        for i in range(len(self.layers) -1, -1, -1):
            (name, value) = self.layers[i]
            #print(i, name, dx.shape)
            #print('W{}'.format(i))
            if i>0:
                m = self.params['W{}'.format(i)].shape[0]
                b = self.params['b{}'.format(i)].shape[0]
            if name=='last':
                #if (self.use_dropout):
                #    dx = dropout_backward(dx, self.masks[i-2])
                dx, dw, db = affine_backward(dx, value)
                grads['W{}'.format(i)] = dw + self.reg * self.params['W{}'.format(i)]
                grads['b{}'.format(i)] = db
            if (name=='relu'):
                if (self.normalization=='batchnorm'):
                    #print('gamma{}'.format(i), name)
                    if (self.use_dropout):
                        dx = dropout_backward(dx, self.masks[i-1])
                    dx, dw, db, dgamma, dbeta = affine_bn_relu_backward(dx, value)
                    grads['W{}'.format(i)] = dw + self.reg * self.params['W{}'.format(i)]
                    grads['b{}'.format(i)] = db
                    grads['gamma{}'.format(i)] = dgamma
                    grads['beta{}'.format(i)] = dbeta
                elif (self.normalization=='layernorm'):
                    if (self.use_dropout):
                        dx = dropout_backward(dx, self.masks[i-1])
                    dx, dw, db, dgamma, dbeta = affine_ln_relu_backward(dx, value)
                    grads['W{}'.format(i)] = dw + self.reg * self.params['W{}'.format(i)]
                    grads['b{}'.format(i)] = db
                    grads['gamma{}'.format(i)] = dgamma
                    grads['beta{}'.format(i)] = dbeta
                else:
                    if (self.use_dropout):
                        dx = dropout_backward(dx, self.masks[i-1])
                    dx, dw, db = affine_relu_backward(dx, value)
                    #print('here',i, name)
                    grads['W{}'.format(i)] = dw + self.reg * self.params['W{}'.format(i)]
                    grads['b{}'.format(i)] = db
            if (name=='first'):
                pass
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################
        return loss, grads
