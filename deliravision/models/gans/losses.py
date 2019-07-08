import torch


class PullAwayLoss(torch.nn.Module):
    """
    Pull Away Loss for the Energy-Based GANs

    See Also
    --------
    `Paper <https://arxiv.org/abs/1609.03126>`_

    """
    def __init__(self, weight=1.):
        """

        Parameters
        ----------
        weight : float
            weight factor (specifying the impact compared to other loss
            functions)
        """
        super().__init__()
        self._weight = weight

    def forward(self, embeddings: torch.Tensor):
        """

        Parameters
        ----------
        embeddings : :class:`torch.Tensor`
            the embeddings of image batches

        Returns
        -------
        :class:`torch.Tensor`
            the loss value

        """
        norm = (embeddings ** 2).sum(-1, keepdim=True).sqrt()
        normalized_emb = embeddings / norm
        similarity = torch.matmul(normalized_emb,
                                  normalized_emb.transpose(0, 1))
        batchsize = embeddings.size(0)

        pt_loss = ((similarity.sum() - batchsize)
                   / (batchsize * (batchsize - 1)))

        return pt_loss * self._weight


class DiscriminatorMarginLoss(torch.nn.Module):
    """
    A loss whose calculation switches slightly depending on a calculated
    margin.

    See Also
    --------
    `Paper <https://arxiv.org/abs/1609.03126>`_

    """
    def __init__(self, divisor=64., loss_fn=torch.nn.MSELoss()):
        super().__init__()
        self._divisor = divisor
        self._loss_fn = loss_fn

    def forward(self, real_recon, real_imgs, fake_recon, fake_imgs):
        """
        Calculates the loss out of the given parameters

        Parameters
        ----------
        real_recon : :class:`torch.Tensor`
            the reconstruction of the real images
        real_imgs : :class:`torch.Tensor`
            the real image batch
        fake_recon : :class:`torch.Tensor`
            the reconstruction of the fake images
        fake_imgs : :class:`torch.Tensor`
            the (generated) fake image batch

        Returns
        -------
        :class:`torch.Tensor`
            the combined (margin-dependent) loss for real and fake images
        :class:`torch.Tensor`
            the loss only for real images
        :class:`torch.Tensor`
            the loss only for fake images
        """
        discr_real = self._loss_fn(real_recon, real_imgs)
        discr_fake = self._loss_fn(fake_recon, fake_imgs)

        margin = max(1., real_imgs.size(0)/self._divisor)

        discr_loss = discr_real

        if (margin - discr_fake).item() > 0:
            discr_loss += margin - discr_fake

        return discr_loss, discr_real, discr_fake
