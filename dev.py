class tools:
    """Various tools to use when developing the Tello drone."""

    def kill_switch(self) -> None:
        """Stops the drone in a emergency."""
        if self.is_flying == True:
            while self.send_control_command("emergency") == False: # Keep sending emergency until accepted
                pass
            self.is_flying = False  # Set API variable to False to quit program.
