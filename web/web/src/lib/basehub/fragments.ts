/* -------------------------------------------------------------------------- */
/*                        Static type definitions                             */
/*  (Replaced basehub fragmentOn with static types for CMS-free operation)    */
/* -------------------------------------------------------------------------- */

export { type AvatarFragment, type AuthorFragment } from "@/common/avatar";

/* -------------------------------------------------------------------------- */
/*                                   Heading                                  */
/* -------------------------------------------------------------------------- */

export interface HeadingFragment {
  title: string;
  subtitle: string | null;
  tag: string | null;
  align: "center" | "left" | "right" | "none" | null;
}

/* -------------------------------------------------------------------------- */
/*                                    Image                                   */
/* -------------------------------------------------------------------------- */

export interface OptimizedImageFragment {
  url: string;
  blurDataURL: string | null;
  aspectRatio: string | null;
  width: number;
  height: number;
  alt: string | null;
}

/* -------------------------------------------------------------------------- */
/*                                    Quote                                   */
/* -------------------------------------------------------------------------- */

export interface QuoteFragment {
  _id: string;
  author: {
    _id: string;
    _title: string;
    image: {
      url: string;
      alt: string | null;
    };
    company: {
      _title: string;
      image: {
        url: string;
        alt: string | null;
      };
    };
    role: string;
  };
  quote: string;
}

/* -------------------------------------------------------------------------- */
/*                                   Button                                   */
/* -------------------------------------------------------------------------- */

export interface ButtonFragment {
  _id: string;
  label: string;
  href: string;
  type: string;
  icon: string | null;
}

/* -------------------------------------------------------------------------- */
/*                              Dark Light Image                              */
/* -------------------------------------------------------------------------- */

export interface DarkLightImageFragment {
  dark: OptimizedImageFragment;
  light: OptimizedImageFragment;
}
