"use client";

import * as React from "react";
import { Track } from "livekit-client";
import { useTrackToggle } from "@livekit/components-react";
import {
  MicrophoneIcon,
  MicrophoneSlashIcon,
  SpinnerIcon,
} from "@phosphor-icons/react/dist/ssr";
import { Toggle } from "@/components/ui/toggle";
import { cn } from "@/lib/utils";

export type TrackToggleProps = React.ComponentProps<typeof Toggle> & {
  source: Parameters<typeof useTrackToggle>[0]["source"];
  pending?: boolean;
};

function getSourceIcon(
  source: Track.Source,
  enabled: boolean,
  pending = false,
) {
  if (pending) {
    return SpinnerIcon;
  }

  switch (source) {
    case Track.Source.Microphone:
      return enabled ? MicrophoneIcon : MicrophoneSlashIcon;
    default:
      return React.Fragment;
  }
}

export function TrackToggle({
  source,
  pressed,
  pending,
  className,
  ...props
}: TrackToggleProps) {
  const IconComponent = getSourceIcon(source, pressed ?? false, pending);

  return (
    <Toggle
      pressed={pressed}
      aria-label={`Toggle ${source}`}
      className={cn(className)}
      {...props}
    >
      <IconComponent weight="bold" className={cn(pending && "animate-spin")} />
      {props.children}
    </Toggle>
  );
}
