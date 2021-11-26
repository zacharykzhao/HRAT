/* This file was generated by SableCC (http://www.sablecc.org/). */

package soot.jimple.parser.node;

import soot.jimple.parser.analysis.*;

@SuppressWarnings("nls")
public final class APrivateModifier extends PModifier
{
    private TPrivate _private_;

    public APrivateModifier()
    {
        // Constructor
    }

    public APrivateModifier(
        @SuppressWarnings("hiding") TPrivate _private_)
    {
        // Constructor
        setPrivate(_private_);

    }

    @Override
    public Object clone()
    {
        return new APrivateModifier(
            cloneNode(this._private_));
    }

    @Override
    public void apply(Switch sw)
    {
        ((Analysis) sw).caseAPrivateModifier(this);
    }

    public TPrivate getPrivate()
    {
        return this._private_;
    }

    public void setPrivate(TPrivate node)
    {
        if(this._private_ != null)
        {
            this._private_.parent(null);
        }

        if(node != null)
        {
            if(node.parent() != null)
            {
                node.parent().removeChild(node);
            }

            node.parent(this);
        }

        this._private_ = node;
    }

    @Override
    public String toString()
    {
        return ""
            + toString(this._private_);
    }

    @Override
    void removeChild(@SuppressWarnings("unused") Node child)
    {
        // Remove child
        if(this._private_ == child)
        {
            this._private_ = null;
            return;
        }

        throw new RuntimeException("Not a child.");
    }

    @Override
    void replaceChild(@SuppressWarnings("unused") Node oldChild, @SuppressWarnings("unused") Node newChild)
    {
        // Replace child
        if(this._private_ == oldChild)
        {
            setPrivate((TPrivate) newChild);
            return;
        }

        throw new RuntimeException("Not a child.");
    }
}
